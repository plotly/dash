import * as R from 'ramda';
import React from 'react';

import { memoizeOne } from 'core/memoizer';
import memoizerCache from 'core/cache/memoizer';
import { Data, IVisibleColumn, VisibleColumns, ActiveCell, SelectedCells, Datum, ColumnId, IViewportOffset, Presentation } from 'dash-table/components/Table/props';
import Cell from 'dash-table/components/Cell';
import isActiveCell from 'dash-table/derived/cell/isActive';
import isSelectedCell from 'dash-table/derived/cell/isSelected';

export default () => new Wrappers().get;

class Wrappers {
    /**
     * Returns the wrapper for each cell in the table.
     */
    get = memoizeOne((
        activeCell: ActiveCell,
        columns: VisibleColumns,
        data: Data,
        offset: IViewportOffset,
        selectedCells: SelectedCells
    ) => R.addIndex<Datum, JSX.Element[]>(R.map)(
        (_, rowIndex) => R.addIndex<IVisibleColumn, JSX.Element>(R.map)(
            (column, columnIndex) => {
                const active = isActiveCell(activeCell, rowIndex + offset.rows, columnIndex + offset.columns);
                const selected = isSelectedCell(selectedCells, rowIndex + offset.rows, columnIndex + offset.columns);

                const isDropdown = column.presentation === Presentation.Dropdown;

                const classes =
                    'dash-cell' +
                    ` column-${columnIndex}` +
                    (active ? ' focused' : '') +
                    (selected ? ' cell--selected' : '') +
                    (isDropdown ? ' dropdown' : '');

                return this.wrapper.get(rowIndex, columnIndex)(
                    active,
                    classes,
                    columnIndex,
                    column.id
                );
            }, columns
        ), data));

    /**
     * Returns the wrapper for a cell.
     */
    private wrapper = memoizerCache<[number, number]>()((
        active: boolean,
        classes: string,
        columnIndex: number,
        columnId: ColumnId
    ) => (<Cell
        active={active}
        classes={classes}
        key={`column-${columnIndex}`}
        property={columnId}
    />));
}