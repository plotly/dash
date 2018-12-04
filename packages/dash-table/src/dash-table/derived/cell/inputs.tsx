import * as R from 'ramda';
import React from 'react';

import { memoizeOneFactory } from 'core/memoizer';

import {
    ActiveCell,
    Data,
    Datum,
    IVisibleColumn,
    VisibleColumns,
    ICellFactoryProps,
    IViewportOffset
} from 'dash-table/components/Table/props';
import CellInput from 'dash-table/components/CellInput';
import derivedCellEventHandlerProps from 'dash-table/derived/cell/eventHandlerProps';
import isActiveCell from 'dash-table/derived/cell/isActive';
import isEditable from './isEditable';

const mapData = R.addIndex<Datum, JSX.Element[]>(R.map);
const mapRow = R.addIndex<IVisibleColumn, JSX.Element>(R.map);

const cellEventHandlerProps = derivedCellEventHandlerProps();

const getter = (
    activeCell: ActiveCell,
    columns: VisibleColumns,
    data: Data,
    offset: IViewportOffset,
    editable: boolean,
    isFocused: boolean,
    tableId: string,
    dropdowns: any[][],
    propsFn: () => ICellFactoryProps
): JSX.Element[][] => mapData(
    (datum, rowIndex) => mapRow(
        (column, columnIndex) => {
            const active = isActiveCell(activeCell, rowIndex + offset.rows, columnIndex + offset.columns);

            const dropdown = dropdowns[rowIndex][columnIndex];
            const handlers = cellEventHandlerProps(propsFn)(rowIndex, columnIndex);

            return (<CellInput
                key={`column-${columnIndex}`}
                active={active}
                clearable={column.clearable}
                datum={datum}
                dropdown={dropdown}
                editable={isEditable(editable, column.editable)}
                focused={isFocused}
                property={column.id}
                tableId={tableId}
                type={column.type}
                value={datum[column.id]}
                {...handlers}
            />);
        },
        columns
    ),
    data
);

export default memoizeOneFactory(getter);
