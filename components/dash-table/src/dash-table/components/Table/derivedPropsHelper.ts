import * as R from 'ramda';

import {memoizeOneWithFlag} from 'core/memoizer';

import QuerySyntaxTree from 'dash-table/syntax-tree/QuerySyntaxTree';

import {
    ControlledTableProps,
    IndexedData,
    SanitizedAndDerivedProps,
    SetProps,
    TableAction
} from './props';

export default () => {
    const filterCache = memoizeOneWithFlag(filter_query => filter_query);
    const paginationCache = memoizeOneWithFlag((page_current, page_size) => [
        page_current,
        page_size
    ]);
    const sortCache = memoizeOneWithFlag(sort => sort);
    const viewportCache = memoizeOneWithFlag(viewport => viewport);
    const viewportSelectedColumnsCache = memoizeOneWithFlag(
        viewport => viewport
    );
    const viewportSelectedRowsCache = memoizeOneWithFlag(viewport => viewport);
    const virtualCache = memoizeOneWithFlag(virtual => virtual);
    const virtualSelectedRowsCache = memoizeOneWithFlag(virtual => virtual);
    const structuredQueryCache = memoizeOneWithFlag((query: string) =>
        new QuerySyntaxTree(query).toStructure()
    );

    return (props: ControlledTableProps, setProps: SetProps) => {
        const {
            filter_query,
            filter_action,
            page_action,
            page_current,
            page_size,
            sort_action,
            sort_by,
            viewport,
            viewport_selected_columns,
            viewport_selected_rows,
            virtual,
            virtual_selected_rows
        } = props;

        const derivedStructureCache = structuredQueryCache(filter_query);

        const viewportCached = viewportCache(viewport).cached;
        const virtualCached = virtualCache(virtual).cached;

        const viewportSelectedColumnsCached = viewportSelectedColumnsCache(
            viewport_selected_columns
        ).cached;
        const viewportSelectedRowsCached = viewportSelectedRowsCache(
            viewport_selected_rows
        ).cached;
        const virtualSelectedRowsCached = virtualSelectedRowsCache(
            virtual_selected_rows
        ).cached;

        const invalidatedFilter = filterCache(filter_query);
        const invalidatedPagination = paginationCache(page_current, page_size);
        const invalidatedSort = sortCache(sort_by);

        const invalidateSelection =
            (!invalidatedFilter.cached &&
                !invalidatedFilter.first &&
                filter_action.type === TableAction.Custom) ||
            (!invalidatedPagination.cached &&
                !invalidatedPagination.first &&
                page_action === TableAction.Custom) ||
            (!invalidatedSort.cached &&
                !invalidatedSort.first &&
                sort_action === TableAction.Custom);

        const newProps: Partial<SanitizedAndDerivedProps> = {};

        if (!derivedStructureCache.cached) {
            newProps.derived_filter_query_structure =
                derivedStructureCache.result;
        }

        if (!virtualCached) {
            newProps.derived_virtual_data = virtual.data;
            newProps.derived_virtual_indices = virtual.indices;
            newProps.derived_virtual_row_ids = R.pluck(
                'id',
                virtual.data as IndexedData
            );
        }

        if (!viewportCached) {
            newProps.derived_viewport_data = viewport.data;
            newProps.derived_viewport_indices = viewport.indices;
            newProps.derived_viewport_row_ids = R.pluck(
                'id',
                viewport.data as IndexedData
            );
        }

        if (!virtualSelectedRowsCached) {
            newProps.derived_virtual_selected_rows = virtual_selected_rows;
            newProps.derived_virtual_selected_row_ids = R.map(
                i => (virtual.data as IndexedData)[i].id,
                virtual_selected_rows
            );
        }

        if (!viewportSelectedColumnsCached) {
            newProps.derived_viewport_selected_columns =
                viewport_selected_columns;
        }

        if (!viewportSelectedRowsCached) {
            newProps.derived_viewport_selected_rows = viewport_selected_rows;
            newProps.derived_viewport_selected_row_ids = R.map(
                i => (viewport.data as IndexedData)[i].id,
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

        setTimeout(() => setProps(newProps), 0);
    };
};
