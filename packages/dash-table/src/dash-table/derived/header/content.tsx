import * as R from 'ramda';
import React from 'react';

import { memoizeOneFactory } from 'core/memoizer';
import { SortDirection, SortBy } from 'core/sorting';
import multiUpdate from 'core/sorting/multi';
import singleUpdate from 'core/sorting/single';

import {
    ColumnId,
    Data,
    SortMode,
    VisibleColumns,
    IVisibleColumn,
    SetProps,
    TableAction,
    SetFilter
} from 'dash-table/components/Table/props';
import * as actions from 'dash-table/utils/actions';
import { SingleColumnSyntaxTree } from 'dash-table/syntax-tree';
import { clearColumnsFilter } from '../filter/map';

const doAction = (
    action: (
        column: IVisibleColumn,
        columns: VisibleColumns,
        columnRowIndex: any,
        mergeDuplicateHeaders: boolean,
        data: Data
    ) => any,
    column: IVisibleColumn,
    columns: VisibleColumns,
    columnRowIndex: any,
    mergeDuplicateHeaders: boolean,
    setFilter: SetFilter,
    setProps: SetProps,
    map: Map<string, SingleColumnSyntaxTree>,
    data: Data
) => () => {
    setProps(action(column, columns, columnRowIndex, mergeDuplicateHeaders, data));

    const affectedColumns: VisibleColumns = [];
    R.forEach(id => {
        const affectedColumn = columns.find(c => c.id === id);
        if (affectedColumn) {
            affectedColumns.push(affectedColumn);
        }
    }, actions.getAffectedColumns(column, columns, columnRowIndex, mergeDuplicateHeaders));

    clearColumnsFilter(map, affectedColumns, setFilter);
};

function doSort(columnId: ColumnId, sortBy: SortBy, mode: SortMode, setProps: SetProps) {
    return () => {
        let direction: SortDirection;
        switch (getSorting(columnId, sortBy)) {
            case SortDirection.Descending:
                direction = SortDirection.None;
                break;
            case SortDirection.Ascending:
                direction = SortDirection.Descending;
                break;
            case SortDirection.None:
                direction = SortDirection.Ascending;
                break;
            default:
                direction = SortDirection.Ascending;
                break;
        }

        const sortingStrategy = mode === SortMode.Single ?
            singleUpdate :
            multiUpdate;

        setProps({
            sort_by: sortingStrategy(
                sortBy,
                { column_id: columnId, direction }
            ),
            ...actions.clearSelection
        });
    };
}

function editColumnName(column: IVisibleColumn, columns: VisibleColumns, columnRowIndex: any, setProps: SetProps, mergeDuplicateHeaders: boolean) {
    return () => {
        setProps(actions.editColumnName(column, columns, columnRowIndex, mergeDuplicateHeaders));
    };
}

function getSorting(columnId: ColumnId, sortBy: SortBy): SortDirection {
    const sort = R.find(s => s.column_id === columnId, sortBy);

    return sort ? sort.direction : SortDirection.None;
}

function getSortingIcon(columnId: ColumnId, sortBy: SortBy) {
    switch (getSorting(columnId, sortBy)) {
        case SortDirection.Descending:
            return '↓';
        case SortDirection.Ascending:
            return '↑';
        case SortDirection.None:
        default:
            return '↕';
    }
}

function getColumnFlag(i: number, flag?: boolean | boolean[]): boolean {
    return typeof flag === 'boolean' ?
        flag :
        !!flag && flag[i];
}

function getter(
    columns: VisibleColumns,
    mergeDuplicateHeaders: boolean,
    data: Data,
    labelsAndIndices: R.KeyValuePair<any[], number[]>[],
    map: Map<string, SingleColumnSyntaxTree>,
    sort_action: TableAction,
    mode: SortMode,
    sortBy: SortBy,
    paginationMode: TableAction,
    setFilter: SetFilter,
    setProps: SetProps,
    merge_duplicate_headers: boolean
): JSX.Element[][] {
    return R.addIndex<R.KeyValuePair<any[], number[]>, JSX.Element[]>(R.map)(
        ([labels, indices], headerRowIndex) => {
            const isLastRow = headerRowIndex === labelsAndIndices.length - 1;

            return R.addIndex<number, JSX.Element>(R.map)(
                columnIndex => {
                    const column = columns[columnIndex];

                    const renamable = getColumnFlag(headerRowIndex, column.renamable);
                    const clearable = paginationMode !== TableAction.Custom && getColumnFlag(headerRowIndex, column.clearable);
                    const deletable = paginationMode !== TableAction.Custom && getColumnFlag(headerRowIndex, column.deletable);

                    return (<div>
                        {sort_action !== TableAction.None && isLastRow ?
                            (<span
                                className='sort'
                                onClick={doSort(column.id, sortBy, mode, setProps)}
                            >
                                {getSortingIcon(column.id, sortBy)}
                            </span>) :
                            ''
                        }

                        {renamable ?
                            (<span
                                className='column-header--edit'
                                onClick={editColumnName(column, columns, headerRowIndex, setProps, merge_duplicate_headers)}
                            />) :
                            ''
                        }

                        {clearable ?
                            (<span
                                className='column-header--clear'
                                onClick={doAction(actions.clearColumn, column, columns, headerRowIndex, mergeDuplicateHeaders, setFilter, setProps, map, data)}
                            />) :
                            ''
                        }

                        {deletable ?
                            (<span
                                className='column-header--delete'
                                onClick={doAction(actions.deleteColumn, column, columns, headerRowIndex, mergeDuplicateHeaders, setFilter, setProps, map, data)}
                            />) :
                            ''
                        }

                        <span className='column-header-name'>{labels[columnIndex]}</span>
                    </div>);
                },
                indices
            );
        },
        labelsAndIndices
    );
}

export default memoizeOneFactory(getter);
