import React, { Component } from 'react';
import PropTypes from 'prop-types';
import * as R from 'ramda';

import Stylesheet from 'core/Stylesheet';
import Cell from 'dash-table/components/Cell';
import * as actions from 'dash-table/utils/actions';

export const DEFAULT_CELL_WIDTH = 200;

const handlers = new Map();

export default class Row extends Component {
    constructor(props) {
        super(props);

        this.getEventHandler = this.getEventHandler.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.handleClick = this.handleClick.bind(this);
        this.handleDoubleClick = this.handleDoubleClick.bind(this);
        this.handlePaste = this.handlePaste.bind(this);
    }

    getEventHandler(fn, idx, i) {
        const fnHandler = (handlers.get(fn) || handlers.set(fn, new Map()).get(fn));
        const idxHandler = (fnHandler.get(idx) || fnHandler.set(idx, new Map()).get(idx));

        return (
            idxHandler.get(i) ||
            (idxHandler.set(i, fn.bind(this, idx, i)).get(i))
        );
    }

    isCellSelected(idx, i) {
        const {
            selected_cell
        } = this.props;

        return R.contains([idx, i], selected_cell);
    }

    handleClick(idx, i, e) {
        const {
            columns,
            editable,
            is_focused,
            selected_cell,
            setProps
        } = this.props;

        const selected = this.isCellSelected(idx, i);

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

        e.preventDefault();
        const cellLocation = [idx, i];
        const newProps = {
            is_focused: false,
            active_cell: cellLocation,
        };

        // visible col indices
        const vci = [];
        columns.forEach((c, i) => {
            if (!c.hidden) {
                vci.push(i);
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
            ).filter(c => R.contains(c[1], vci));
        } else {
            newProps.selected_cell = [cellLocation];
        }
        setProps(newProps);
    }

    handleDoubleClick(idx, i, e) {
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
                is_focused: true,
            };
            setProps(newProps);
        }
    }

    handleChange(idx, i, e) {
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
            dataframe: newDataframe,
        });
    }

    handlePaste(idx, i, e) {
        const {
            is_focused,
        } = this.props;

        const selected = this.isCellSelected(idx, i);

        if (!(selected && is_focused)) {
            e.preventDefault();
        }
    }

    renderSelectableRow() {
        const {
            idx,
            n_fixed_columns,
            setProps,
            selected_rows,
            row_deletable,
            row_selectable
        } = this.props;

        const rowSelectableFixedIndex = row_deletable ? 1 : 0;

        return !row_selectable ? null : (
            <td
                className={
                    'select-cell ' +
                    (n_fixed_columns > rowSelectableFixedIndex ? `frozen-left frozen-left-${rowSelectableFixedIndex} ` : '')
                }
                style={n_fixed_columns > rowSelectableFixedIndex ? {
                    width: `30px`
                } : {}}
            >
                <input
                    type={row_selectable === 'single' ? 'radio' : 'checkbox'}
                    name="row-select"
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
            </td>
        );
    }

    renderDeletableRow() {
        const {
            idx,
            n_fixed_columns,
            setProps,
            row_deletable,
        } = this.props;

        return !row_deletable ? null : (
            <td
                className={
                    'delete-cell ' +
                    (n_fixed_columns > 0 ? 'frozen-left frozen-left-0 ' : '')
                }
                onClick={() => setProps(actions.deleteRow(idx, this.props))}
                style={n_fixed_columns > 0 ? {
                    width: `30px`
                } : {}}
            >
                {'×'}
            </td>
        );
    }

    renderCells() {
        const {
            active_cell,
            columns,
            dataframe,
            dropdown_properties,
            idx,
            editable,
            is_focused,
            n_fixed_columns,
            row_deletable,
            row_selectable
        } = this.props;

        const visibleColumns = columns.filter(column => !column.hidden);

        const columnIndexOffset =
            (row_deletable ? 1 : 0) +
            (row_selectable ? 1 : 0);

        return columns.map((column, i) => {
            if (column.hidden) {
                return null;
            }

            const visibleIndex = visibleColumns.indexOf(column) + columnIndexOffset;
            const isFixed = visibleIndex < n_fixed_columns;

            const classes = [
                ...(isFixed ? [`frozen-left`, `frozen-left-${visibleIndex}`] : []),
                ...[`column-${visibleIndex}`]
            ];

            const width = `${Stylesheet.unit(column.width || DEFAULT_CELL_WIDTH, 'px')}`;

            const style = Object.assign({},
                (isFixed ? { maxWidth: width, minWidth: width, width: width } : {})
            );

            const dropdown = ((
                dropdown_properties &&
                dropdown_properties[column.id] &&
                (dropdown_properties[column.id].length > idx ? dropdown_properties[column.id][idx] : null)
            ) || column || {}).options;

            return (<Cell
                key={`${column.id}-${i}`}
                active={active_cell[0] === idx && active_cell[1] === i}
                classes={classes}
                clearable={column.clearable}
                dropdown={dropdown}
                editable={editable}
                focused={is_focused}
                onClick={this.getEventHandler(this.handleClick, idx, i)}
                onDoubleClick={this.getEventHandler(this.handleDoubleClick, idx, i)}
                onPaste={this.getEventHandler(this.handlePaste, idx, i)}
                onChange={this.getEventHandler(this.handleChange, idx, i)}
                selected={this.isCellSelected(idx, i)}
                style={style}
                type={column.type}
                value={dataframe[idx][column.id]}
            />);
        });
    }

    render() {
        const {
            idx,
            selected_rows
        } = this.props;

        const rowSelectable = this.renderSelectableRow();
        const deleteCell = this.renderDeletableRow();

        const cells = this.renderCells();

        return (
            <tr
                className={R.contains(idx, selected_rows) ? 'selected-row' : ''}
            >
                {deleteCell}
                {rowSelectable}
                {cells}
            </tr>
        );
    }
}

Row.propTypes = {
    columns: PropTypes.any,
    dataframe: PropTypes.any,
    idx: PropTypes.any,
    dropdown_properties: PropTypes.any,
    editable: PropTypes.any,
    is_focused: PropTypes.any,
    setProps: PropTypes.any,
    selected_cell: PropTypes.any,
    active_cell: PropTypes.any,
    n_fixed_columns: PropTypes.any,
    selected_rows: PropTypes.any,
    row_deletable: PropTypes.bool,
    row_selectable: PropTypes.any
};
