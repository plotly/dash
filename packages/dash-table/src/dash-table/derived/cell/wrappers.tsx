import * as R from 'ramda';
import React, { MouseEvent } from 'react';

import { memoizeOne } from 'core/memoizer';
import memoizerCache from 'core/cache/memoizer';
import { Data, IVisibleColumn, VisibleColumns, ActiveCell, SelectedCells, Datum, ColumnId, IViewportOffset, Presentation, ICellFactoryProps } from 'dash-table/components/Table/props';
import Cell from 'dash-table/components/Cell';
import derivedCellEventHandlerProps, { Handler } from 'dash-table/derived/cell/eventHandlerProps';
import isActiveCell from 'dash-table/derived/cell/isActive';
import isSelectedCell from 'dash-table/derived/cell/isSelected';

export default (propsFn: () => ICellFactoryProps) => new Wrappers(propsFn).get;

class Wrappers {
    constructor(
        propsFn: () => ICellFactoryProps,
        private readonly handlers = derivedCellEventHandlerProps(propsFn)
    ) {

    }

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
                    column.id,
                    rowIndex,
                    this.handlers(Handler.Enter, rowIndex, columnIndex),
                    this.handlers(Handler.Leave, rowIndex, columnIndex),
                    this.handlers(Handler.Move, rowIndex, columnIndex)
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
        columnId: ColumnId,
        rowIndex: number,
        onEnter: (e: MouseEvent) => void,
        onLeave: (e: MouseEvent) => void,
        onMove: (e: MouseEvent) => void
    ) => (<Cell
        active={active}
        attributes={{
            'data-dash-column': columnId,
            'data-dash-row': rowIndex
        }}
        classes={classes}
        key={`column-${columnIndex}`}
        onMouseEnter={onEnter}
        onMouseLeave={onLeave}
        onMouseMove={onMove}
    />));
}
