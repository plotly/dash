import * as R from 'ramda';
import React from 'react';

import { memoizeOneFactory } from 'core/memoizer';
import { SortDirection, SortSettings } from 'core/sorting';
import multiUpdateSettings from 'core/sorting/multi';
import singleUpdateSettings from 'core/sorting/single';

import {
    ColumnId,
    PaginationMode,
    SortingType,
    VisibleColumns,
    IVisibleColumn,
    SetProps,
    ControlledTableProps,
    Sorting
} from 'dash-table/components/Table/props';
import * as actions from 'dash-table/utils/actions';

function deleteColumn(column: IVisibleColumn, columns: VisibleColumns, columnRowIndex: any, setProps: SetProps, options: ControlledTableProps) {
    return () => {
        setProps(actions.deleteColumn(column, columns, columnRowIndex, options));
    };
}

function doSort(columnId: ColumnId, sortSettings: SortSettings, sortType: SortingType, setProps: SetProps) {
    return () => {
        let direction: SortDirection;
        switch (getSorting(columnId, sortSettings)) {
            case SortDirection.Descending:
                direction = SortDirection.Ascending;
                break;
            case SortDirection.Ascending:
                direction = SortDirection.None;
                break;
            case SortDirection.None:
            default:
                direction = SortDirection.Descending;
                break;
        }

        const sortingStrategy = sortType === 'single' ?
            singleUpdateSettings :
            multiUpdateSettings;

        setProps({
            sorting_settings: sortingStrategy(
                sortSettings,
                { columnId, direction }
            )
        });
    };
}

function editColumnName(column: IVisibleColumn, columns: VisibleColumns, columnRowIndex: any, setProps: SetProps, options: ControlledTableProps) {
    return () => {
        setProps(actions.editColumnName(column, columns, columnRowIndex, options));
    };
}

function getSorting(columnId: ColumnId, settings: SortSettings): SortDirection {
    const setting = R.find(s => s.columnId === columnId, settings);

    return setting ? setting.direction : SortDirection.None;
}

function getSortingIcon(columnId: ColumnId, sortSettings: SortSettings) {
    switch (getSorting(columnId, sortSettings)) {
        case SortDirection.Descending:
            return '↑';
        case SortDirection.Ascending:
            return '↓';
        case SortDirection.None:
        default:
            return '↕';
    }
}

function getter(
    columns: VisibleColumns,
    labelsAndIndices: R.KeyValuePair<any[], number[]>[],
    sorting: Sorting,
    sortType: SortingType,
    sortSettings: SortSettings,
    paginationMode: PaginationMode,
    setProps: SetProps,
    options: ControlledTableProps
): JSX.Element[][] {
    return R.addIndex<R.KeyValuePair<any[], number[]>, JSX.Element[]>(R.map)(
        ([labels, indices], headerRowIndex) => {
            const isLastRow = headerRowIndex === labelsAndIndices.length - 1;

            return R.addIndex<number, JSX.Element>(R.map)(
                columnIndex => {
                    const column = columns[columnIndex];

                    const editable = (column.editable_name && R.type(column.editable_name) === 'Boolean') ||
                        (R.type(column.editable_name) === 'Number' && column.editable_name === headerRowIndex);

                    const deletable = paginationMode !== 'be' &&
                        (
                            (column.deletable && R.type(column.deletable) === 'Boolean') ||
                            (R.type(column.deletable) === 'Number' && column.deletable === headerRowIndex)
                        );

                    return (<div>
                        {sorting && isLastRow ?
                            (<span
                                className='sort'
                                onClick={doSort(column.id, sortSettings, sortType, setProps)}
                            >
                                {getSortingIcon(column.id, sortSettings)}
                            </span>) :
                            ''
                        }

                        {editable ?
                            (<span
                                className='column-header--edit'
                                onClick={editColumnName(column, columns, headerRowIndex, setProps, options)}
                            >
                                {`✎`}
                            </span>) :
                            ''
                        }

                        {deletable ?
                            (<span
                                className='column-header--delete'
                                onClick={deleteColumn(column, columns, headerRowIndex, setProps, options)}
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
