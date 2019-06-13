import React, { Component } from 'react';
import * as R from 'ramda';

/*#if DEV*/
import Logger from 'core/Logger';
/*#endif*/

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
    SetProps,
    IState,
    StandaloneState,
    SanitizedAndDerivedProps,
    TableAction
} from './props';

import 'react-select/dist/react-select.css';
import './Table.less';
import './Dropdown.css';
import { isEqual } from 'core/comparer';
import { SingleColumnSyntaxTree } from 'dash-table/syntax-tree';
import derivedFilterMap from 'dash-table/derived/filter/map';

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
                    props.columns
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
                    nextProps.columns
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
            filter_query,
            filter_action,
            page_action,
            page_current,
            page_size,
            selected_rows,
            sort_action,
            sort_by,
            uiCell,
            uiHeaders,
            uiViewport,
            virtualization
        } = R.merge(this.props, this.state) as (SanitizedAndDerivedProps & StandaloneState);

        const virtual = this.virtual(
            columns,
            data,
            filter_action,
            filter_query,
            sort_action,
            sort_by
        );

        const viewport = this.viewport(
            page_action,
            page_current,
            page_size,
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
            page_action,
            page_current,
            page_size,
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
            filter_query,
            filter_action,
            page_action,
            page_current,
            page_size,
            sort_action,
            sort_by,
            viewport,
            viewport_selected_rows,
            virtual,
            virtual_selected_rows
        } = controlled;

        const derivedStructureCache = this.structuredQueryCache(filter_query);

        const viewportCached = this.viewportCache(viewport).cached;
        const virtualCached = this.virtualCache(virtual).cached;

        const viewportSelectedRowsCached = this.viewportSelectedRowsCache(viewport_selected_rows).cached;
        const virtualSelectedRowsCached = this.virtualSelectedRowsCache(virtual_selected_rows).cached;

        const invalidatedFilter = this.filterCache(filter_query);
        const invalidatedPagination = this.paginationCache(page_current, page_size);
        const invalidatedSort = this.sortCache(sort_by);

        const invalidateSelection =
            (!invalidatedFilter.cached && !invalidatedFilter.first && filter_action === TableAction.Custom) ||
            (!invalidatedPagination.cached && !invalidatedPagination.first && page_action === TableAction.Custom) ||
            (!invalidatedSort.cached && !invalidatedSort.first && sort_action === TableAction.Custom);

        const { controlledSetProps } = this;
        let newProps: Partial<SanitizedAndDerivedProps> = {};

        if (!derivedStructureCache.cached) {
            newProps.derived_filter_structure = derivedStructureCache.result;
        }

        if (!virtualCached) {
            newProps.derived_virtual_data = virtual.data;
            newProps.derived_virtual_indices = virtual.indices;
            newProps.derived_virtual_row_ids = R.pluck('id', virtual.data);
        }

        if (!viewportCached) {
            newProps.derived_viewport_data = viewport.data;
            newProps.derived_viewport_indices = viewport.indices;
            newProps.derived_viewport_row_ids = R.pluck('id', viewport.data);
        }

        if (!virtualSelectedRowsCached) {
            newProps.derived_virtual_selected_rows = virtual_selected_rows;
            newProps.derived_virtual_selected_row_ids = R.map(
                i => virtual.data[i].id,
                virtual_selected_rows
            );
        }

        if (!viewportSelectedRowsCached) {
            newProps.derived_viewport_selected_rows = viewport_selected_rows;
            newProps.derived_viewport_selected_row_ids = R.map(
                i => viewport.data[i].id,
                viewport_selected_rows
            );
        }

        if (invalidateSelection) {
            newProps.active_cell = undefined;
            newProps.selected_cells = [];
            newProps.start_cell = undefined;
            newProps.end_cell = undefined;
            newProps.selected_rows = [];
            newProps.selected_row_ids = [];
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
    private readonly paginator = derivedPaginator();
    private readonly viewport = derivedViewportData();
    private readonly viewportSelectedRows = derivedSelectedRows();
    private readonly virtual = derivedVirtualData();
    private readonly virtualSelectedRows = derivedSelectedRows();
    private readonly virtualized = derivedVirtualizedData();
    private readonly visibleColumns = derivedVisibleColumns();

    private readonly filterCache = memoizeOneWithFlag(filter_query => filter_query);
    private readonly paginationCache = memoizeOneWithFlag((page_current, page_size) => [page_current, page_size]);
    private readonly sortCache = memoizeOneWithFlag(sort => sort);
    private readonly viewportCache = memoizeOneWithFlag(viewport => viewport);
    private readonly viewportSelectedRowsCache = memoizeOneWithFlag(viewport => viewport);
    private readonly virtualCache = memoizeOneWithFlag(virtual => virtual);
    private readonly virtualSelectedRowsCache = memoizeOneWithFlag(virtual => virtual);
    private readonly structuredQueryCache = memoizeOneWithFlag(
        (query: string) => new QuerySyntaxTree(query).toStructure()
    );
}
