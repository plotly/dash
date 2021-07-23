import React, {Component} from 'react';
import * as R from 'ramda';

/*#if DEV*/
import Logger from 'core/Logger';
/*#endif*/

import {memoizeOne} from 'core/memoizer';

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
import {SingleColumnSyntaxTree} from 'dash-table/syntax-tree';
import derivedFilterMap from 'dash-table/derived/filter/map';

import controlledPropsHelper from './controlledPropsHelper';
import derivedPropsHelper from './derivedPropsHelper';
import DOM from 'core/browser/DOM';
import shouldComponentUpdate from './shouldComponentUpdate';

export default class Table extends Component<
    SanitizedAndDerivedProps,
    StandaloneState
> {
    constructor(props: SanitizedAndDerivedProps) {
        super(props);

        this.state = {
            workFilter: {
                value: props.filter_query,
                map: this.filterMap(
                    new Map<string, SingleColumnSyntaxTree>(),
                    props.filter_action.operator,
                    props.filter_query,
                    props.visibleColumns
                )
            },
            rawFilterQuery: '',
            scrollbarWidth: 0
        };
    }

    UNSAFE_componentWillReceiveProps(nextProps: SanitizedAndDerivedProps) {
        this.setState(state => {
            const {
                applyFocus: currentApplyFocus,
                workFilter: {map: currentMap, value}
            } = state;

            const nextState: Partial<StandaloneState> = {};

            // state for filter
            if (nextProps.filter_query !== this.props.filter_query) {
                if (value !== nextProps.filter_query) {
                    const map = this.filterMap(
                        currentMap,
                        nextProps.filter_action.operator,
                        nextProps.filter_query,
                        nextProps.visibleColumns
                    );

                    if (map !== currentMap) {
                        nextState.workFilter = {map, value};
                    }
                }
            }

            // state for applying focus
            if (nextProps.active_cell !== this.props.active_cell) {
                nextState.applyFocus = true;
            } else if (nextProps.loading_state !== this.props.loading_state) {
                const activeElement = document.activeElement as HTMLElement;
                const tdElement = DOM.getFirstParentOfType(activeElement, 'td');
                const tableElement = DOM.getParentById(
                    tdElement,
                    this.props.id
                );

                nextState.applyFocus = !!tableElement;
            }

            if (nextState.applyFocus === currentApplyFocus) {
                delete nextState.applyFocus;
            }

            return R.keysIn(nextState).length ? (nextState as any) : null;
        });
    }

    shouldComponentUpdate(nextProps: any, nextState: any) {
        const props: any = this.props;
        const state: any = this.state;

        return shouldComponentUpdate(props, nextProps, state, nextState);
    }

    render() {
        const controlled = this.controlledPropsHelper(
            this.controlledSetProps,
            this.controlledSetState,
            this.props,
            this.state
        );

        this.updateDerivedProps(controlled, this.controlledSetProps);

        return <ControlledTable {...controlled} />;
    }

    private get controlledSetProps() {
        return this.__setProps(this.props.setProps);
    }

    private get controlledSetState() {
        return this.__setState();
    }

    private readonly __setProps = memoizeOne((setProps?: SetProps) => {
        return setProps
            ? (newProps: Partial<SanitizedAndDerivedProps>) => {
                  /*#if DEV*/
                  const props: any = this.props;
                  R.forEach(
                      key =>
                          props[key] === (newProps as any)[key] &&
                          Logger.fatal(`Updated prop ${key} was mutated`),
                      R.keysIn(newProps)
                  );
                  /*#endif*/

                  if (R.has('data', newProps)) {
                      const {data} = this.props;

                      newProps.data_timestamp = Date.now();
                      newProps.data_previous = data;
                  }

                  setProps(newProps);
              }
            : (newProps: Partial<SanitizedAndDerivedProps>) => {
                  /*#if DEV*/
                  const props: any = this.state;
                  R.forEach(
                      key =>
                          props[key] === (newProps as any)[key] &&
                          Logger.fatal(`Updated prop ${key} was mutated`),
                      R.keysIn(newProps)
                  );
                  /*#endif*/

                  this.setState(newProps);
              };
    });

    private readonly __setState = memoizeOne(
        () => (state: Partial<IState>) => this.setState(state as IState)
    );

    private readonly filterMap = derivedFilterMap();

    private readonly controlledPropsHelper = controlledPropsHelper();
    private readonly updateDerivedProps = derivedPropsHelper();
}
