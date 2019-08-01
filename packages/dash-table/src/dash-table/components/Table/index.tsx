import React, { Component } from 'react';
import * as R from 'ramda';

/*#if DEV*/
import Logger from 'core/Logger';
/*#endif*/

import { memoizeOne } from 'core/memoizer';

import ControlledTable from 'dash-table/components/ControlledTable';

import {
    SetProps,
    IState,
    StandaloneState,
    SanitizedAndDerivedProps
} from './props';

import 'react-select/dist/react-select.css';
import './Table.less';
import './style';
import './Dropdown.css';
import { isEqual } from 'core/comparer';
import { SingleColumnSyntaxTree } from 'dash-table/syntax-tree';
import derivedFilterMap from 'dash-table/derived/filter/map';

import controlledPropsHelper from './controlledPropsHelper';
import derivedPropsHelper from './derivedPropsHelper';

const DERIVED_REGEX = /^derived_/;

export default class Table extends Component<SanitizedAndDerivedProps, StandaloneState> {
    constructor(props: SanitizedAndDerivedProps) {
        super(props);

        this.state = {
            forcedResizeOnly: false,
            workFilter: {
                value: props.filter_query,
                map: this.filterMap(
                    new Map<string, SingleColumnSyntaxTree>(),
                    props.filter_query,
                    props.visibleColumns
                )
            },
            rawFilterQuery: '',
            scrollbarWidth: 0
        };
    }

    componentWillReceiveProps(nextProps: SanitizedAndDerivedProps) {
        if (nextProps.filter_query === this.props.filter_query) {
            return;
        }

        this.setState(state => {
            const { workFilter: { map: currentMap, value } } = state;

            if (value !== nextProps.filter_query) {
                const map = this.filterMap(
                    currentMap,
                    nextProps.filter_query,
                    nextProps.visibleColumns
                );

                return map !== currentMap ? { workFilter: { map, value} } : null;
            } else {
                return null;
            }
        });
    }

    shouldComponentUpdate(nextProps: any, nextState: any) {
        const props: any = this.props;
        const state: any = this.state;

        return R.any(key =>
            !DERIVED_REGEX.test(key) && props[key] !== nextProps[key],
            R.keysIn(props)
        ) || !isEqual(state, nextState);
    }

    render() {
        let controlled = this.controlledPropsHelper(
            this.controlledSetProps,
            this.controlledSetState,
            this.props,
            this.state
        );

        this.updateDerivedProps(controlled, this.controlledSetProps);

        return (<ControlledTable {...controlled} />);
    }

    private get controlledSetProps() {
        return this.__setProps(this.props.setProps);
    }

    private get controlledSetState() {
        return this.__setState();
    }

    private readonly __setProps = memoizeOne((setProps?: SetProps) => {
        return setProps ? (newProps: any) => {
            /*#if DEV*/
            const props: any = this.props;
            R.forEach(
                key => props[key] === newProps[key] && Logger.fatal(`Updated prop ${key} was mutated`),
                R.keysIn(newProps)
            );
            /*#endif*/

            if (R.has('data', newProps)) {
                const { data } = this.props;

                newProps.data_timestamp = Date.now();
                newProps.data_previous = data;
            }

            setProps(newProps);
        } : (newProps: Partial<SanitizedAndDerivedProps>) => {
            /*#if DEV*/
            const props: any = this.state;
            R.forEach(
                key => props[key] === (newProps as any)[key] && Logger.fatal(`Updated prop ${key} was mutated`),
                R.keysIn(newProps)
            );
            /*#endif*/

            this.setState(newProps);
        };
    });

    private readonly __setState = memoizeOne(() => (state: Partial<IState>) => this.setState(state as IState));

    private readonly filterMap = derivedFilterMap();

    private readonly controlledPropsHelper = controlledPropsHelper();
    private readonly updateDerivedProps = derivedPropsHelper();
}
