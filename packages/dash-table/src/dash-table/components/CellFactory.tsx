import * as R from 'ramda';
import React from 'react';

import Cell from 'dash-table/components/Cell';
import { ICellFactoryOptions, SelectedCells } from 'dash-table/components/Table/props';
import * as actions from 'dash-table/utils/actions';

export default class CellFactory {
    private readonly handlers = new Map();

    private get props() {
        return this.propsFn();
    }

    constructor(private readonly propsFn: () => ICellFactoryOptions) {

    }

    private isCellSelected = (selectedCells: SelectedCells, idx: number, i: number) => {
        return selectedCells && R.contains([idx, i], selectedCells);
    }

    private getEventHandler = (fn: Function, idx: number, i: number): any => {
        const fnHandler = (this.handlers.get(fn) || this.handlers.set(fn, new Map()).get(fn));
        const idxHandler = (fnHandler.get(idx) || fnHandler.set(idx, new Map()).get(idx));

        return (
            idxHandler.get(i) ||
            (idxHandler.set(i, fn.bind(this, idx, i)).get(i))
        );
    }

    private handleClick = (idx: number, i: number, e: any) => {
        const {
            columns,
            editable,
            is_focused,
            row_deletable,
            row_selectable,
            selected_cell,
            setProps
        } = this.props;

        const selected = this.isCellSelected(selected_cell, idx, i);

        if (!editable) {
            return;
        }
        if (!is_focused) {
            e.preventDefault();
        }

        // don't update if already selected
        if (selected) {
            return;
        }

        // visible col indices
        const columnIndexOffset =
            (row_deletable ? 1 : 0) +
            (row_selectable ? 1 : 0);

        e.preventDefault();
        const cellLocation: [number, number] = [idx, i + columnIndexOffset];
        const newProps: Partial<ICellFactoryOptions> = {
            is_focused: false,
            active_cell: cellLocation
        };

        const vci: any[] = [];
        columns.forEach((c, ci: number) => {
            if (!c.hidden) {
                vci.push(ci + columnIndexOffset);
            }
        });

        const selectedRows = R.uniq(R.pluck(0, selected_cell)).sort();
        const selectedCols = R.uniq(R.pluck(1, selected_cell)).sort();
        const minRow = selectedRows[0];
        const minCol = selectedCols[0];

        if (e.shiftKey) {
            newProps.selected_cell = R.xprod(
                R.range(
                    R.min(minRow, cellLocation[0]),
                    R.max(minRow, cellLocation[0]) + 1
                ),
                R.range(
                    R.min(minCol, cellLocation[1]),
                    R.max(minCol, cellLocation[1]) + 1
                )
            ).filter(c => R.contains(c[1], vci)) as any;
        } else {
            newProps.selected_cell = [cellLocation];
        }

        setProps(newProps);
    }

    private handleDoubleClick = (idx: number, i: number, e: any) => {
        const {
            editable,
            is_focused,
            setProps
        } = this.props;

        if (!editable) {
            return;
        }

        if (!is_focused) {
            e.preventDefault();
            const newProps = {
                selected_cell: [[idx, i]],
                active_cell: [idx, i],
                is_focused: true
            };
            setProps(newProps);
        }
    }

    private handleChange = (idx: number, i: number, e: any) => {
        const {
            columns,
            dataframe,
            editable,
            setProps
        } = this.props;

        const c = columns[i];

        if (!editable) {
            return;
        }

        const newDataframe = R.set(
            R.lensPath([idx, c.id]),
            e.target.value,
            dataframe
        );
        setProps({
            dataframe: newDataframe
        });
    }

    private handlePaste = (idx: number, i: number, e: any) => {
        const {
            is_focused,
            selected_cell
        } = this.props;

        const selected = this.isCellSelected(selected_cell, idx, i);

        if (!(selected && is_focused)) {
            e.preventDefault();
        }
    }

    private rowSelectCell(idx: number) {
        const {
            setProps,
            selected_rows,
            row_selectable
        } = this.props;

        return !row_selectable ? null : (<td
            key='select'
            className='select-cell'
            style={{ width: `30px`, maxWidth: `30px`, minWidth: `30px` }}
        >
            <input
                type={row_selectable === 'single' ? 'radio' : 'checkbox'}
                name='row-select'
                checked={R.contains(idx, selected_rows)}
                onChange={() => setProps({
                    selected_rows:
                        row_selectable === 'single' ?
                            [idx] :
                            R.ifElse(
                                R.contains(idx),
                                R.without([idx]),
                                R.append(idx)
                            )(selected_rows)
                })}
            />
        </td>);
    }

    private rowDeleteCell(idx: number) {
        const {
            setProps,
            row_deletable
        } = this.props;

        return !row_deletable ? null : (<td
            key='delete'
            className='delete-cell'
            onClick={() => setProps(actions.deleteRow(idx, this.props))}
            style={{ width: `30px`, maxWidth: `30px`, minWidth: `30px` }}
        >
            {'×'}
        </td>);
    }

    public createCells() {
        const {
            active_cell,
            columns,
            column_conditional_dropdowns,
            column_conditional_styles,
            column_static_dropdown,
            column_static_style,
            editable,
            id,
            is_focused,
            row_deletable,
            row_selectable,
            selected_cell,
            virtualizer
        } = this.props;

        const { dataframe, indices } = virtualizer;

        const visibleColumns = columns.filter(column => !column.hidden);

        const offset =
            (row_deletable ? 1 : 0) +
            (row_selectable ? 1 : 0);

        return dataframe.map((datum, virtualIdx) => {
            const realIdx = indices[virtualIdx];

            const deleteCell = this.rowDeleteCell(realIdx);
            const selectCell = this.rowSelectCell(realIdx);

            const cells = visibleColumns.map((column, visibleIndex) => {
                visibleIndex += offset;

                const index = columns.indexOf(column);

                const classes = [`column-${index + offset}`];

                let conditionalDropdowns = column_conditional_dropdowns.find((cd: any) => cd.id === column.id);
                let staticDropdown = column_static_dropdown.find((sd: any) => sd.id === column.id);

                conditionalDropdowns = conditionalDropdowns && conditionalDropdowns.dropdowns;
                staticDropdown = staticDropdown && staticDropdown.dropdown;

                let conditionalStyles = column_conditional_styles.find((cs: any) => cs.id === column.id);
                let staticStyle = column_static_style.find((ss: any) => ss.id === column.id);

                conditionalStyles = conditionalStyles && conditionalStyles.styles;
                staticStyle = staticStyle && staticStyle.style;

                return (<Cell
                    key={`${column.id}-${visibleIndex}`}
                    active={active_cell[0] === virtualIdx && active_cell[1] === index + offset}
                    classes={classes}
                    clearable={column.clearable}
                    conditionalDropdowns={conditionalDropdowns}
                    conditionalStyles={conditionalStyles}
                    datum={datum}
                    editable={editable}
                    focused={!!is_focused}
                    onClick={this.getEventHandler(this.handleClick, virtualIdx, index)}
                    onDoubleClick={this.getEventHandler(this.handleDoubleClick, virtualIdx, index)}
                    onPaste={this.getEventHandler(this.handlePaste, virtualIdx, index)}
                    onChange={this.getEventHandler(this.handleChange, realIdx, index)}
                    property={column.id}
                    selected={R.contains([virtualIdx, index + offset], selected_cell)}
                    staticDropdown={staticDropdown}
                    staticStyle={staticStyle}
                    tableId={id}
                    type={column.type}
                    value={datum[column.id]}
                />);
            });

            if (selectCell) {
                cells.unshift(selectCell);
            }

            if (deleteCell) {
                cells.unshift(deleteCell);
            }

            return cells;
        });
    }
}