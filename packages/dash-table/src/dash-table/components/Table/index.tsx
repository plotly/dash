import React, { Component } from 'react';
import * as R from 'ramda';

import { memoizeOne, memoizeOneWithFlag } from 'core/memoizer';

import ControlledTable from 'dash-table/components/ControlledTable';

import derivedPaginator from 'dash-table/derived/paginator';
import derivedViewportData from 'dash-table/derived/data/viewport';
import derivedVirtualData from 'dash-table/derived/data/virtual';
import derivedVisibleColumns from 'dash-table/derived/column/visible';

import {
    ControlledTableProps,
    PropsWithDefaultsAndDerived,
    SetProps
} from './props';

import 'react-select/dist/react-select.css';
import './Table.less';
import './Dropdown.css';

const DERIVED_REGEX = /^derived_/;

export default class Table extends Component<PropsWithDefaultsAndDerived> {
    private controlled: ControlledTableProps;

    constructor(props: PropsWithDefaultsAndDerived) {
        super(props);

        this.controlled = this.getControlledProps(this.props);
        this.updateDerivedProps();
    }

    componentWillReceiveProps(nextProps: PropsWithDefaultsAndDerived) {
        this.controlled = this.getControlledProps(nextProps);
        this.updateDerivedProps();
    }

    shouldComponentUpdate(nextProps: any) {
        const props: any = this.props;

        return R.any(key =>
            !DERIVED_REGEX.test(key) && props[key] !== nextProps[key],
            R.keysIn(props)
        );
    }

    render() {
        return (<ControlledTable {...this.controlled} />);
    }

    private getControlledProps(props: PropsWithDefaultsAndDerived): ControlledTableProps {
        const { setProps } = this;

        const {
            columns,
            data,
            filtering,
            filtering_settings,
            pagination_mode,
            pagination_settings,
            sorting,
            sorting_settings,
            sorting_treat_empty_string_as_none
        } = props;

        const virtual = this.virtual(
            data,
            filtering,
            filtering_settings,
            sorting,
            sorting_settings,
            sorting_treat_empty_string_as_none
        );

        const viewport = this.viewport(
            pagination_mode,
            pagination_settings,
            virtual.data,
            virtual.indices
        );

        const paginator = this.paginator(
            pagination_mode,
            pagination_settings,
            setProps,
            virtual.data
        );

        const visibleColumns = this.visibleColumns(columns);

        return R.mergeAll([
            props,
            {
                columns: visibleColumns,
                paginator,
                setProps,
                viewport,
                virtual
            }
        ]);
    }

    private updateDerivedProps() {
        const { filtering, filtering_settings, pagination_mode, pagination_settings, sorting, sorting_settings, viewport, virtual } = this.controlled;

        const viewportCached = this.viewportCache(viewport).cached;
        const virtualCached = this.virtualCache(virtual).cached;

        const invalidatedFilter = this.filterCache(filtering_settings);
        const invalidatedPagination = this.paginationCache(pagination_settings);
        const invalidatedSort = this.sortCache(sorting_settings);

        const invalidateSelection =
            (!invalidatedFilter.cached && !invalidatedFilter.first && filtering === 'be') ||
            (!invalidatedPagination.cached && !invalidatedPagination.first && pagination_mode === 'be') ||
            (!invalidatedSort.cached && !invalidatedSort.first && sorting === 'be');

        if (virtualCached && viewportCached && !invalidateSelection) {
            return;
        }

        const { setProps } = this;
        let newProps: Partial<PropsWithDefaultsAndDerived> = {};

        if (!virtualCached) {
            newProps.derived_virtual_data = virtual.data;
            newProps.derived_virtual_indices = virtual.indices;
        }

        if (!viewportCached) {
            newProps.derived_viewport_data = viewport.data;
            newProps.derived_viewport_indices = viewport.indices;
        }

        if (invalidateSelection) {
            newProps.active_cell = undefined;
            newProps.selected_cell = undefined;
            newProps.selected_rows = undefined;
        }

        setTimeout(() => setProps(newProps), 0);
    }

    private get setProps() {
        return this.__setProps(this.props.setProps);
    }

    private readonly __setProps = memoizeOne((setProps?: SetProps) => {
        return setProps ? (newProps: any) => {
            if (R.has('data', newProps)) {
                const { data } = this.props;

                newProps.data_timestamp = Date.now();
                newProps.data_previous = data;
            }

            setProps(newProps);
        } : (newProps: Partial<PropsWithDefaultsAndDerived>) => this.setState(newProps);
    });

    private readonly paginator = derivedPaginator();
    private readonly viewport = derivedViewportData();
    private readonly virtual = derivedVirtualData();
    private readonly visibleColumns = derivedVisibleColumns();

    private readonly filterCache = memoizeOneWithFlag(filter => filter);
    private readonly paginationCache = memoizeOneWithFlag(pagination => pagination);
    private readonly sortCache = memoizeOneWithFlag(sort => sort);
    private readonly viewportCache = memoizeOneWithFlag(viewport => viewport);
    private readonly virtualCache = memoizeOneWithFlag(virtual => virtual);
}