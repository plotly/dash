import * as R from 'ramda';

import derivedPaginator from 'dash-table/derived/paginator';
import derivedSelectedColumns from 'dash-table/derived/selects/columns';
import derivedSelectedRows from 'dash-table/derived/selects/rows';
import derivedViewportData from 'dash-table/derived/data/viewport';
import derivedVirtualData from 'dash-table/derived/data/virtual';
import derivedVirtualizedData from 'dash-table/derived/data/virtualized';

import {
    ControlledTableProps,
    SanitizedAndDerivedProps,
    SetProps,
    SetState,
    StandaloneState
} from './props';

export default () => {
    const getPaginator = derivedPaginator();
    const getViewport = derivedViewportData();
    const getViewportSelectedColumns = derivedSelectedColumns();
    const getViewportSelectedRows = derivedSelectedRows();
    const getVirtual = derivedVirtualData();
    const getVirtualSelectedRows = derivedSelectedRows();
    const getVirtualized = derivedVirtualizedData();

    return (
        setProps: SetProps,
        setState: SetState,
        props: SanitizedAndDerivedProps,
        state: StandaloneState
    ) => {
        const {
            data,
            filter_query,
            filter_action,
            page_action,
            page_current,
            page_size,
            page_count,
            selected_columns,
            selected_rows,
            sort_action,
            sort_by,
            uiCell,
            uiHeaders,
            uiViewport,
            virtualization,
            visibleColumns
        } = R.mergeRight(props, state) as SanitizedAndDerivedProps &
            StandaloneState;

        const virtual = getVirtual(
            visibleColumns,
            data,
            filter_action,
            filter_query,
            sort_action,
            sort_by
        );

        const viewport = getViewport(
            page_action,
            page_current,
            page_size,
            virtual.data,
            virtual.indices
        );

        const virtualized = getVirtualized(
            virtualization,
            uiCell,
            uiHeaders,
            uiViewport,
            viewport
        );

        const virtual_selected_rows = getVirtualSelectedRows(
            virtual.indices,
            selected_rows
        );

        const viewport_selected_columns = getViewportSelectedColumns(
            visibleColumns,
            selected_columns
        );

        const viewport_selected_rows = getViewportSelectedRows(
            viewport.indices,
            selected_rows
        );

        const paginator = getPaginator(
            page_action,
            page_current,
            page_size,
            page_count,
            setProps,
            virtual.data
        );

        return R.mergeAll([
            props,
            state,
            {
                paginator,
                setProps,
                setState,
                viewport,
                viewport_selected_columns,
                viewport_selected_rows,
                virtual,
                virtual_selected_rows,
                virtualized
            }
        ]) as ControlledTableProps;
    };
};
