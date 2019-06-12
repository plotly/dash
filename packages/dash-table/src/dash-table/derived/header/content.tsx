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
    TableAction
} from 'dash-table/components/Table/props';
import * as actions from 'dash-table/utils/actions';

function deleteColumn(column: IVisibleColumn, columns: VisibleColumns, columnRowIndex: any, setProps: SetProps, data: Data) {
    return () => {
        setProps(actions.deleteColumn(column, columns, columnRowIndex, data));
    };
}

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

function editColumnName(column: IVisibleColumn, columns: VisibleColumns, columnRowIndex: any, setProps: SetProps) {
    return () => {
        setProps(actions.editColumnName(column, columns, columnRowIndex));
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

function getter(
    columns: VisibleColumns,
    data: Data,
    labelsAndIndices: R.KeyValuePair<any[], number[]>[],
    sort_action: TableAction,
    mode: SortMode,
    sortBy: SortBy,
    paginationMode: TableAction,
    setProps: SetProps
): JSX.Element[][] {
    return R.addIndex<R.KeyValuePair<any[], number[]>, JSX.Element[]>(R.map)(
        ([labels, indices], headerRowIndex) => {
            const isLastRow = headerRowIndex === labelsAndIndices.length - 1;

            return R.addIndex<number, JSX.Element>(R.map)(
                columnIndex => {
                    const column = columns[columnIndex];

                    const renamable: boolean = typeof column.renamable === 'boolean' ?
                        column.renamable :
                        !!column.renamable && column.renamable[headerRowIndex];

                    const deletable = paginationMode !== TableAction.Custom && (
                        typeof column.deletable === 'boolean' ?
                            column.deletable :
                            !!column.deletable && column.deletable[headerRowIndex]
                    );

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
                                onClick={editColumnName(column, columns, headerRowIndex, setProps)}
                            >
                                {`✎`}
                            </span>) :
                            ''
                        }

                        {deletable ?
                            (<span
                                className='column-header--delete'
                                onClick={deleteColumn(column, columns, headerRowIndex, setProps, data)}
                            >
                                {'×'}
                            </span>) :
                            ''
                        }

                        <span>{labels[columnIndex]}</span>
                    </div>);
                },
                indices
            );
        },
        labelsAndIndices
    );
}

export default memoizeOneFactory(getter);
