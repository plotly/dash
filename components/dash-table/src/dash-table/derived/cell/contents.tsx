import * as R from 'ramda';
import React from 'react';

import {
    ICellCoordinates,
    Data,
    Datum,
    ICellFactoryProps,
    IDropdown,
    IDropdownValue,
    IViewportOffset,
    IColumn,
    Presentation,
    Columns
} from 'dash-table/components/Table/props';
import CellInput from 'dash-table/components/CellInput';
import derivedCellEventHandlerProps, {
    Handler
} from 'dash-table/derived/cell/eventHandlerProps';
import CellLabel from 'dash-table/components/CellLabel';
import CellDropdown from 'dash-table/components/CellDropdown';
import {memoizeOne} from 'core/memoizer';
import getFormatter from 'dash-table/type/formatter';
import {shallowClone} from 'core/math/matrixZipMap';
import CellMarkdown from 'dash-table/components/CellMarkdown';
import Markdown from 'dash-table/utils/Markdown';

const mapData = R.addIndex<Datum, JSX.Element[]>(R.map);
const mapRow = R.addIndex<IColumn, JSX.Element>(R.map);

enum CellType {
    Dropdown,
    DropdownLabel,
    Input,
    Label,
    Markdown
}

function getCellType(
    active: boolean,
    editable: boolean,
    dropdown: IDropdownValue[] | undefined,
    presentation: Presentation | undefined,
    is_loading: boolean
): CellType {
    switch (presentation) {
        case Presentation.Input:
            return !active || !editable || is_loading
                ? CellType.Label
                : CellType.Input;
        case Presentation.Dropdown:
            return !dropdown || !editable
                ? CellType.DropdownLabel
                : CellType.Dropdown;
        case Presentation.Markdown:
            return CellType.Markdown;
        default:
            return !active || !editable || is_loading
                ? CellType.Label
                : CellType.Input;
    }
}

export default (propsFn: () => ICellFactoryProps) => new Contents(propsFn);

class Contents {
    private cell_selectable: boolean;
    constructor(
        propsFn: () => ICellFactoryProps,
        private readonly handlers = derivedCellEventHandlerProps(propsFn)
    ) {
        this.cell_selectable = propsFn().cell_selectable;
    }

    partialGet = memoizeOne(
        (
            columns: Columns,
            data: Data,
            _offset: IViewportOffset,
            isFocused: boolean,
            dropdowns: (IDropdown | undefined)[][],
            data_loading: boolean,
            markdown: Markdown
        ): JSX.Element[][] => {
            const formatters = R.map(getFormatter, columns);

            return mapData(
                (datum, rowIndex) =>
                    mapRow(
                        (column, columnIndex) =>
                            this.getContent(
                                false,
                                false,
                                isFocused,
                                column,
                                dropdowns && dropdowns[rowIndex][columnIndex],
                                columnIndex,
                                rowIndex,
                                datum,
                                formatters,
                                data_loading,
                                markdown
                            ),
                        columns
                    ),
                data
            );
        }
    );

    get = memoizeOne(
        (
            contents: JSX.Element[][],
            activeCell: ICellCoordinates | undefined,
            applyFocus: boolean,
            columns: Columns,
            data: Data,
            offset: IViewportOffset,
            isFocused: boolean,
            dropdowns: (IDropdown | undefined)[][],
            data_loading: boolean,
            markdown: Markdown
        ): JSX.Element[][] => {
            if (!activeCell) {
                return contents;
            }

            const {row: iActive, column: jActive} = activeCell;
            const i = iActive - offset.rows;
            const j = jActive - offset.columns;

            if (i < 0 || j < 0 || data.length <= i || columns.length <= j) {
                return contents;
            }

            const formatters = R.map(getFormatter, columns);

            contents = shallowClone(contents);
            contents[i][j] = this.getContent(
                true,
                applyFocus || false,
                isFocused,
                columns[j],
                dropdowns && dropdowns[i][j],
                jActive,
                iActive,
                data[i],
                formatters,
                data_loading,
                markdown
            );

            return contents;
        }
    );

    private getContent(
        active: boolean,
        applyFocus: boolean,
        isFocused: boolean,
        column: IColumn,
        dropdown: IDropdown | undefined,
        columnIndex: number,
        rowIndex: number,
        datum: any,
        formatters: ((value: any) => any)[],
        data_loading: boolean,
        markdown: Markdown
    ) {
        const className = [
            ...(active ? ['input-active'] : []),
            isFocused ? 'focused' : 'unfocused',
            ...(this.cell_selectable ? ['selectable'] : []),
            'dash-cell-value'
        ].join(' ');

        const cellType = getCellType(
            active,
            column.editable,
            dropdown && dropdown.options,
            column.presentation,
            data_loading
        );
        switch (cellType) {
            case CellType.Dropdown:
                return (
                    <CellDropdown
                        key={`column-${columnIndex}`}
                        active={active}
                        applyFocus={applyFocus}
                        clearable={dropdown && dropdown.clearable}
                        dropdown={dropdown && dropdown.options}
                        onChange={this.handlers(
                            Handler.Change,
                            rowIndex,
                            columnIndex
                        )}
                        value={datum[column.id]}
                        disabled={data_loading}
                    />
                );
            case CellType.Input:
                return (
                    <CellInput
                        key={`column-${columnIndex}`}
                        active={active}
                        applyFocus={applyFocus}
                        className={className}
                        focused={isFocused}
                        onChange={this.handlers(
                            Handler.Change,
                            rowIndex,
                            columnIndex
                        )}
                        onMouseUp={this.handlers(
                            Handler.MouseUp,
                            rowIndex,
                            columnIndex
                        )}
                        onPaste={this.handlers(
                            Handler.Paste,
                            rowIndex,
                            columnIndex
                        )}
                        type={column.type}
                        value={datum[column.id]}
                    />
                );
            case CellType.Markdown:
                return (
                    <CellMarkdown
                        key={`column-${columnIndex}`}
                        active={active}
                        applyFocus={applyFocus}
                        className={className}
                        markdown={markdown}
                        value={datum[column.id]}
                    />
                );
            case CellType.DropdownLabel:
            case CellType.Label:
            default:
                const resolvedValue =
                    cellType === CellType.DropdownLabel
                        ? this.resolveDropdownLabel(dropdown, datum[column.id])
                        : formatters[columnIndex](datum[column.id]);

                return (
                    <CellLabel
                        active={active}
                        applyFocus={applyFocus}
                        className={className}
                        key={`column-${columnIndex}`}
                        value={resolvedValue}
                    />
                );
        }
    }

    private resolveDropdownLabel(dropdown: IDropdown | undefined, value: any) {
        const dropdownValue =
            dropdown &&
            dropdown.options &&
            dropdown.options.find(option => option.value === value);

        return dropdownValue ? dropdownValue.label : value;
    }
}
