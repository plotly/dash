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
    IViewportOffset,
    ColumnType,
    DropdownValues
} from 'dash-table/components/Table/props';
import CellInput from 'dash-table/components/CellInput';
import derivedCellEventHandlerProps from 'dash-table/derived/cell/eventHandlerProps';
import isActiveCell from 'dash-table/derived/cell/isActive';
import isCellEditable from './isEditable';
import CellLabel from 'dash-table/components/CellLabel';
import CellDropdown from 'dash-table/components/CellDropdown';

const mapData = R.addIndex<Datum, JSX.Element[]>(R.map);
const mapRow = R.addIndex<IVisibleColumn, JSX.Element>(R.map);

const cellEventHandlerProps = derivedCellEventHandlerProps();

enum CellType {
    Dropdown,
    Input,
    Label
}

function getCellType(
    active: boolean,
    editable: boolean,
    dropdown: DropdownValues | undefined,
    type: ColumnType = ColumnType.Text
) {
    switch (type) {
        case ColumnType.Text:
        case ColumnType.Numeric:
            return (!active || !editable) ? CellType.Label : CellType.Input;
        case ColumnType.Dropdown:
            return (!dropdown || !editable) ? CellType.Label : CellType.Dropdown;
        default:
            return CellType.Label;
    }
}

const getter = (
    activeCell: ActiveCell,
    columns: VisibleColumns,
    data: Data,
    offset: IViewportOffset,
    editable: boolean,
    isFocused: boolean,
    dropdowns: (DropdownValues | undefined)[][],
    propsFn: () => ICellFactoryProps
): JSX.Element[][] => mapData(
    (datum, rowIndex) => mapRow(
        (column, columnIndex) => {
            const active = isActiveCell(activeCell, rowIndex + offset.rows, columnIndex + offset.columns);

            const dropdown = dropdowns[rowIndex][columnIndex];
            const handlers = cellEventHandlerProps(propsFn)(rowIndex, columnIndex);

            const isEditable = isCellEditable(editable, column.editable);

            const className = [
                ...(active ? ['input-active'] : []),
                ...(isFocused ? ['focused'] : ['unfocused']),
                ...['dash-cell-value']
            ].join(' ');

            switch (getCellType(active, isEditable, dropdown, column.type)) {
                case CellType.Dropdown:
                    return (<CellDropdown
                        key={`column-${columnIndex}`}
                        active={active}
                        clearable={column.clearable}
                        dropdown={dropdown}
                        onChange={handlers.onChange}
                        value={datum[column.id]}
                    />);
                case CellType.Input:
                    return (<CellInput
                        key={`column-${columnIndex}`}
                        active={active}
                        className={className}
                        focused={isFocused}
                        onChange={handlers.onChange}
                        onClick={handlers.onClick}
                        onDoubleClick={handlers.onDoubleClick}
                        onMouseUp={handlers.onMouseUp}
                        onPaste={handlers.onPaste}
                        type={column.type}
                        value={datum[column.id]}
                    />);
                case CellType.Label:
                default:
                    return (<CellLabel
                        className={className}
                        key={`column-${columnIndex}`}
                        onClick={handlers.onClick}
                        onDoubleClick={handlers.onDoubleClick}
                        value={datum[column.id]}
                    />);
            }
        },
        columns
    ),
    data
);

export default memoizeOneFactory(getter);
