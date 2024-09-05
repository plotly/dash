import * as R from 'ramda';
import React from 'react';

import memoizerCache from 'core/cache/memoizer';
import derivedCellEventHandlerProps, {
    Handler
} from 'dash-table/derived/cell/eventHandlerProps';
import {
    ColumnId,
    Columns,
    ICellFactoryProps
} from 'dash-table/components/Table/props';

class Wrappers {
    constructor(
        propsFn: () => ICellFactoryProps,
        private readonly handlers = derivedCellEventHandlerProps(propsFn)
    ) {}

    get = (
        columns: Columns,
        labelsAndIndices: R.KeyValuePair<any[], number[]>[],
        mergeHeaders: boolean
    ): JSX.Element[][] =>
        labelsAndIndices.map(([labels, indices], rowIndex) =>
            indices.map((columnIndex, i) => {
                const column = columns[columnIndex];

                let colSpan: number;
                if (!mergeHeaders) {
                    colSpan = 1;
                } else {
                    if (columnIndex === R.last(indices)) {
                        colSpan = labels.length - columnIndex;
                    } else {
                        colSpan = indices[i + 1] - columnIndex;
                    }
                }

                return this.wrapper.get(rowIndex, columnIndex)(
                    columnIndex,
                    column.id,
                    colSpan,
                    columnIndex === columns.length - 1 ||
                        columnIndex === R.last(indices),
                    this.handlers(Handler.EnterHeader, rowIndex, columnIndex),
                    this.handlers(Handler.Leave, rowIndex, columnIndex),
                    this.handlers(Handler.MoveHeader, rowIndex, columnIndex)
                );
            })
        );

    /**
     * Returns the wrapper for a header cell.
     */
    private wrapper = memoizerCache<[number, number]>()(
        (
            columnIndex: number,
            columnId: ColumnId,
            colSpan: number,
            lastIndex: boolean,
            onEnter: (e: MouseEvent) => void,
            onLeave: (e: MouseEvent) => void,
            onMove: (e: MouseEvent) => void
        ) => (
            <th
                key={`header-cell-${columnIndex}`}
                data-dash-column={columnId}
                colSpan={colSpan}
                className={
                    'dash-header ' +
                    `column-${columnIndex} ` +
                    (lastIndex ? 'cell--right-last ' : '')
                }
                onMouseEnter={onEnter as any}
                onMouseLeave={onLeave as any}
                onMouseMove={onMove as any}
            />
        )
    );
}

export default (propsFn: () => ICellFactoryProps) => new Wrappers(propsFn);
