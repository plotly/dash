import React, { Component } from 'react';
import * as R from 'ramda';

import { memoizeOne, memoizeOneWithFlag } from 'core/memoizer';

import ControlledTable from 'dash-table/components/ControlledTable';

import derivedPaginator from 'dash-table/derived/paginator';
import derivedSelectedRows from 'dash-table/derived/selectedRows';
import derivedViewportData from 'dash-table/derived/data/viewport';
import derivedVirtualData from 'dash-table/derived/data/virtual';
import derivedVirtualizedData from 'dash-table/derived/data/virtualized';
import derivedVisibleColumns from 'dash-table/derived/column/visible';

import QuerySyntaxTree from 'dash-table/syntax-tree/QuerySyntaxTree';

import {
    ControlledTableProps,
    PropsWithDefaultsAndDerived,
    SetProps,
    IState,
    StandaloneState,
    PropsWithDefaults
} from './props';

import 'react-select/dist/react-select.css';
import './Table.less';
import './Dropdown.css';
import { isEqual } from 'core/comparer';
/*#if DEV*/
import Logger from 'core/Logger';
/*#endif*/

const DERIVED_REGEX = /^derived_/;

export default class Table extends Component<PropsWithDefaultsAndDerived, StandaloneState> {
    constructor(props: PropsWithDefaultsAndDerived) {
        super(props);

        this.state = {
            forcedResizeOnly: false,
            rawFilterQuery: '',
            scrollbarWidth: 0
        };
    }

    shouldComponentUpdate(nextProps: any, nextState: any) {
        const props: any = this.props;
        const state: any = this.state;

        return R.any(key =>
            !DERIVED_REGEX.test(key) && props[key] !== nextProps[key],
            R.keysIn(props)
        ) || !isEqual(state, nextState, false);
    }

    render() {
        let controlled = this.getControlledProps();
        this.updateDerivedProps(controlled);

        return (<ControlledTable {...controlled} />);
    }

    private getControlledProps(): ControlledTableProps {
        const {
            controlledSetProps: setProps,
            controlledSetState: setState
        } = this;

        const {
            columns,
            data,
            filter,
            filtering,
            pagination_mode,
            pagination_settings,
            selected_rows,
            sorting,
            sorting_settings,
            sorting_treat_empty_string_as_none,
            uiCell,
            uiHeaders,
            uiViewport,
            virtualization
        } = R.merge(this.props, this.state) as (PropsWithDefaults & StandaloneState);

        const virtual = this.virtual(
            data,
            filtering,
            filter,
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

        const virtualized = this.virtualized(
            virtualization,
            uiCell,
            uiHeaders,
            uiViewport,
            viewport
        );

        const virtual_selected_rows = this.virtualSelectedRows(
            virtual.indices,
            selected_rows
        );

        const viewport_selected_rows = this.viewportSelectedRows(
            viewport.indices,
            selected_rows
        );

        const paginator = this.paginator(
            pagination_mode,
            pagination_settings,
            setProps,
            virtual.data
        );

        const visibleColumns = this.visibleColumns(columns);

        return R.mergeAll([
            this.props,
            this.state,
            {
                columns: visibleColumns,
                paginator,
                setProps,
                setState,
                viewport,
                viewport_selected_rows,
                virtual,
                virtual_selected_rows,
                virtualized
            }
        ]) as ControlledTableProps;
    }

    private updateDerivedProps(controlled: ControlledTableProps) {
        const {
            filter,
            filtering,
            pagination_mode,
            pagination_settings,
            sorting,
            sorting_settings,
            viewport,
            viewport_selected_rows,
            virtual,
            virtual_selected_rows
        } = controlled;

        const derivedStructureCache = this.structuredQueryCache(filter);

        const viewportCached = this.viewportCache(viewport).cached;
        const virtualCached = this.virtualCache(virtual).cached;

        const viewportSelectedRowsCached = this.viewportSelectedRowsCache(viewport_selected_rows).cached;
        const virtualSelectedRowsCached = this.virtualSelectedRowsCache(virtual_selected_rows).cached;

        const invalidatedFilter = this.filterCache(filter);
        const invalidatedPagination = this.paginationCache(pagination_settings);
        const invalidatedSort = this.sortCache(sorting_settings);

        const invalidateSelection =
            (!invalidatedFilter.cached && !invalidatedFilter.first && filtering === 'be') ||
            (!invalidatedPagination.cached && !invalidatedPagination.first && pagination_mode === 'be') ||
            (!invalidatedSort.cached && !invalidatedSort.first && sorting === 'be');

        const { controlledSetProps } = this;
        let newProps: Partial<PropsWithDefaultsAndDerived> = {};

        if (!derivedStructureCache.cached) {
            newProps.derived_filter_structure = derivedStructureCache.result;
        }

        if (!virtualCached) {
            newProps.derived_virtual_data = virtual.data;
            newProps.derived_virtual_indices = virtual.indices;
        }

        if (!viewportCached) {
            newProps.derived_viewport_data = viewport.data;
            newProps.derived_viewport_indices = viewport.indices;
        }

        if (!virtualSelectedRowsCached) {
            newProps.derived_virtual_selected_rows = virtual_selected_rows;
        }

        if (!viewportSelectedRowsCached) {
            newProps.derived_viewport_selected_rows = viewport_selected_rows;
        }

        if (invalidateSelection) {
            newProps.active_cell = undefined;
            newProps.selected_cells = undefined;
            newProps.selected_rows = undefined;
        }

        if (!R.keys(newProps).length) {
            return;
        }

        setTimeout(() => controlledSetProps(newProps), 0);
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
        } : (newProps: Partial<PropsWithDefaultsAndDerived>) => {
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

    private readonly paginator = derivedPaginator();
    private readonly viewport = derivedViewportData();
    private readonly viewportSelectedRows = derivedSelectedRows();
    private readonly virtual = derivedVirtualData();
    private readonly virtualSelectedRows = derivedSelectedRows();
    private readonly virtualized = derivedVirtualizedData();
    private readonly visibleColumns = derivedVisibleColumns();

    private readonly filterCache = memoizeOneWithFlag(filter => filter);
    private readonly paginationCache = memoizeOneWithFlag(pagination => pagination);
    private readonly sortCache = memoizeOneWithFlag(sort => sort);
    private readonly viewportCache = memoizeOneWithFlag(viewport => viewport);
    private readonly viewportSelectedRowsCache = memoizeOneWithFlag(viewport => viewport);
    private readonly virtualCache = memoizeOneWithFlag(virtual => virtual);
    private readonly virtualSelectedRowsCache = memoizeOneWithFlag(virtual => virtual);
    private readonly structuredQueryCache = memoizeOneWithFlag(
        (query: string) => new QuerySyntaxTree(query).toStructure()
    );
}