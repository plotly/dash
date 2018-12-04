import * as R from 'ramda';
import React from 'react';

import { memoizeAll, memoizeOne } from 'core/memoizer';
import { Data, IVisibleColumn, VisibleColumns, ColumnType, ActiveCell, SelectedCells, Datum, ColumnId, IViewportOffset } from 'dash-table/components/Table/props';
import Cell from 'dash-table/components/Cell';
import isActiveCell from 'dash-table/derived/cell/isActive';
import isSelectedCell from 'dash-table/derived/cell/isSelected';
import memoizerCache from 'core/memoizerCache';

type Key = [number, number];
type ElementCacheFn = (
    key: Key,
    active: boolean,
    classes: string,
    columnIndex: number,
    columnId: ColumnId
) => JSX.Element;

function getter(
    elementCache: ElementCacheFn,
    activeCell: ActiveCell,
    columns: VisibleColumns,
    data: Data,
    offset: IViewportOffset,
    selectedCells: SelectedCells
): JSX.Element[][] {
    return R.addIndex<Datum, JSX.Element[]>(R.map)(
        (_, rowIndex) => R.addIndex<IVisibleColumn, JSX.Element>(R.map)(
            (column, columnIndex) => {
                const active = isActiveCell(activeCell, rowIndex + offset.rows, columnIndex + offset.columns);
                const selected = isSelectedCell(selectedCells, rowIndex + offset.rows, columnIndex + offset.columns);

                const classes =
                    'dash-cell' +
                    ` column-${columnIndex}` +
                    (active ? ' focused' : '') +
                    (selected ? ' cell--selected' : '') +
                    (column.type === ColumnType.Dropdown ? ' dropdown' : '');

                return elementCache([rowIndex, columnIndex], active, classes, columnIndex, column.id);
            },
            columns
        ),
        data
    );
}

function decorator(_id: string): ((
    activeCell: ActiveCell,
    columns: VisibleColumns,
    data: Data,
    offset: IViewportOffset,
    selectedCells: SelectedCells
) => JSX.Element[][]) {
    const elementCache = memoizerCache<Key, [boolean, string, number, ColumnId], JSX.Element>(
        (active: boolean, classes: string, columnIndex: number, columnId: ColumnId) => (<Cell
            active={active}
            classes={classes}
            key={`column-${columnIndex}`}
            property={columnId}
        />)
    );

    return memoizeOne(getter).bind(undefined, elementCache);
}

export default memoizeAll(decorator);
