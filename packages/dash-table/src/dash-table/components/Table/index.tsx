import React, { Component } from 'react';
import * as R from 'ramda';

import { memoizeOne } from 'core/memoizer';

import VirtualizationFactory from 'dash-table/virtualization/Factory';

import ControlledTable from 'dash-table/components/ControlledTable';
import { PropsWithDefaults, SetProps } from './props';
import VirtualizationAdapter from './VirtualizationAdapter';

import 'react-select/dist/react-select.css';
import './Table.less';
import './Dropdown.css';

export default class Table extends Component<PropsWithDefaults> {
    constructor(props: any) {
        super(props);
    }

    public get setProps() {
        return this.__setProps(this.props.setProps);
    }

    render() {
        const { setProps, virtualizer } = this;

        virtualizer.refresh();

        return (<ControlledTable
            {...R.mergeAll([
                this.props,
                this.state,
                { setProps, virtualizer }
            ])}
        />);
    }

    private get adapter() {
        return this.__adapter();
    }

    private get virtualizer() {
        const { virtualization, virtualization_settings } = this.props;

        return this.__virtualizer(
            virtualization,
            virtualization_settings
        );
    }

    private __adapter = memoizeOne(
        () => new VirtualizationAdapter(this)
    );

    private __setProps = memoizeOne((setProps?: SetProps) => {
        return setProps ? (newProps: any) => {
            if (R.has('dataframe', newProps)) {
                const { dataframe } = this.props;

                newProps.dataframe_timestamp = Date.now();
                newProps.dataframe_previous = dataframe;
            }

            setProps(newProps);
        } : (newProps: Partial<PropsWithDefaults>) => this.setState(newProps);
    });

    private __virtualizer = memoizeOne((_virtualization, _settings) => {
        return VirtualizationFactory.getVirtualizer(this.adapter);
    });
}