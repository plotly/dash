import React, {Component} from 'react';
import PropTypes from 'prop-types';
import * as R from 'ramda';
import SheetClip from 'sheetclip';
import Row from './Row.js';
import Header from './Header.js';
import {colIsEditable} from './derivedState';
import {
    KEY_CODES,
    isCtrlMetaKey,
    isCtrlDown,
    isMetaKey,
    isNavKey,
} from '../utils/unicode';
import {selectionCycle} from '../utils/navigation';
import computedStyles from './computedStyles';

import 'react-select/dist/react-select.css';
import './Table.css';
import './Dropdown.css';

export default class Table extends Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    render() {
        if (!this.props.setProps) {
            const newProps = R.mergeAll([
                this.props,
                this.state,
                {
                    setProps: newProps => this.setState(newProps),
                    this: 'that'
                }
            ]);
            console.warn('newProps', newProps);
            return <ControlledTable {...newProps}/>
        } else {
            return <ControlledTable {...R.merge(
                this.props,
                {
                    setProps: newProps => {
                        if (R.has('dataframe', newProps)) {
                            newProps.dataframe_timestamp = Date.now()
                        }
                        this.props.setProps(newProps);
                    }
                }
            )}/>
        }
    }
}

class ControlledTable extends Component {
    constructor(props) {
        super(props);

        this.handleKeyDown = this.handleKeyDown.bind(this);
        this.collectRows = this.collectRows.bind(this);
        this.onPaste = this.onPaste.bind(this);
    }

    componentDidMount() {
        if (
            this.props.selected_cell.length &&
            !R.contains(this.props.active_cell, this.props.selected_cell)
        ) {
            this.props.setProps({active_cell: this.props.selected_cell[0]});
        }
    }

    handleKeyDown(e) {
        const {
            active_cell,
            columns,
            setProps,
            is_focused,
            editable,
        } = this.props;

        console.warn(`handleKeyDown: ${e.key}`);

        const ctrlDown = isCtrlDown(e);

        // if this is the initial CtrlMeta keydown with no modifiers then pass
        if (isCtrlMetaKey(e.keyCode)) {
            return;
        }

        // if paste event onPaste handler registered in Table jsx handles it
        if (ctrlDown && e.keyCode === KEY_CODES.V) {
            return;
        }

        // copy
        if (e.keyCode === KEY_CODES.C && ctrlDown && !is_focused) {
            this.onCopy(e);
            return;
        }

        if (e.keyCode === KEY_CODES.ESCAPE) {
            setProps({is_focused: false});
            return;
        }

        if (
            e.keyCode === KEY_CODES.ENTER &&
            !is_focused &&
            colIsEditable(editable, columns[active_cell[1]])
        ) {
            setProps({is_focused: true});
            return;
        }

        if (
            is_focused &&
            (e.keyCode !== KEY_CODES.TAB && e.keyCode !== KEY_CODES.ENTER)
        ) {
            return;
        }

        if (isNavKey(e.keyCode)) {
            this.switchCell(e);
            return;
        }

        if (
            e.keyCode === KEY_CODES.BACKSPACE ||
            e.keyCode === KEY_CODES.DELETE
        ) {
            this.deleteCell(e);
        }
        // if we have any non-meta key enter editable mode
        else if (
            !this.props.is_focused &&
            colIsEditable(editable, columns[active_cell[1]]) &&
            !isMetaKey(e.keyCode)
        ) {
            setProps({is_focused: true});
        }

        return;
    }

    switchCell(event) {
        const e = event;
        const {
            active_cell,
            columns,
            dataframe,
            selected_cell,
            setProps,
        } = this.props;

        const hasSelection = selected_cell.length > 1;
        const isEnterOrTab =
            e.keyCode === KEY_CODES.ENTER || e.keyCode === KEY_CODES.TAB;

        // If we have a multi-cell selection and are using ENTER or TAB
        // move active cell within the selection context.
        if (hasSelection && isEnterOrTab) {
            const nextCell = this.getNextCell(e, {
                currentCell: active_cell,
                restrictToSelection: true,
            });
            setProps({
                is_focused: false,
                active_cell: nextCell,
            });
            return;
        }

        // If we are not extending selection with shift and are
        // moving with navigation keys cancel selection and move.
        else if (!e.shiftKey) {
            const nextCell = this.getNextCell(e, {
                currentCell: active_cell,
                restrictToSelection: false,
            });
            setProps({
                is_focused: false,
                selected_cell: [nextCell],
                active_cell: nextCell,
            });
            return;
        }

        // else we are navigating with arrow keys and extending selection
        // with shift.
        let targetCells = [];
        let removeCells = [];
        const selectedRows = R.uniq(R.pluck(0, selected_cell)).sort();
        const selectedCols = R.uniq(R.pluck(1, selected_cell)).sort();

        const minRow = selectedRows[0];
        const minCol = selectedCols[0];
        const maxRow = selectedRows[selectedRows.length - 1];
        const maxCol = selectedCols[selectedCols.length - 1];

        // visible col indices
        const vci = [];
        columns.forEach((c, i) => {
            if (!c.hidden) {
                vci.push(i);
            }
        });

        const selectingDown =
            e.keyCode === KEY_CODES.ARROW_DOWN || e.keyCode === KEY_CODES.ENTER;
        const selectingUp = e.keyCode === KEY_CODES.ARROW_UP;
        const selectingRight =
            e.keyCode === KEY_CODES.ARROW_RIGHT || e.keyCode === KEY_CODES.TAB;
        const selectingLeft = e.keyCode === KEY_CODES.ARROW_LEFT;

        // If there are selections above the active cell and we are
        // selecting down then pull down the top selection towards
        // the active cell.
        if (selectingDown && active_cell[0] > minRow) {
            removeCells = selectedCols.map(col => [minRow, col]);
        }

        // Otherwise if we are selecting down select the next row if possible.
        else if (selectingDown && maxRow !== dataframe.length - 1) {
            targetCells = selectedCols.map(col => [maxRow + 1, col]);
        }

        // If there are selections below the active cell and we are selecting
        // up remove lower row.
        else if (selectingUp && active_cell[0] < maxRow) {
            removeCells = selectedCols.map(col => [maxRow, col]);
        }

        // Otherwise if we are selecting up select next row if possible.
        else if (selectingUp && minRow > 0) {
            targetCells = selectedCols.map(col => [minRow - 1, col]);
        }

        // If there are selections to the right of the active cell and
        // we are selecting left, move the right side closer to active_cell
        else if (selectingLeft && active_cell[1] < maxCol) {
            removeCells = selectedRows.map(row => [row, maxCol]);
        }

        // Otherwise increase the selection left if possible
        else if (selectingLeft && minCol > 0) {
            targetCells = selectedRows.map(row => [row, minCol - 1]);
        }

        // If there are selections to the left of the active cell and
        // we are selecting right, move the left side closer to active_cell
        else if (selectingRight && active_cell[1] > minCol) {
            removeCells = selectedRows.map(row => [row, minCol]);
        }

        // Otherwise move selection right if possible
        else if (selectingRight && maxCol + 1 <= R.last(vci)) {
            targetCells = selectedRows.map(row => [row, maxCol + 1]);
        }

        const newSelectedCell = R.without(
            removeCells,
            R.uniq(R.concat(targetCells, selected_cell))
        );
        setProps({
            is_focused: false,
            selected_cell: newSelectedCell,
        });
    }

    deleteCell(event) {
        const {
            columns,
            dataframe,
            editable,
            selected_cell,
            setProps,
        } = this.props;

        event.preventDefault();

        let newDataframe = dataframe;
        selected_cell.forEach(cell => {
            if (colIsEditable(editable, columns[cell[1]])) {
                newDataframe = R.set(
                    R.lensPath([cell[0], columns[cell[1]].id]),
                    '',
                    newDataframe
                );
            }
        });

        setProps({
            dataframe: newDataframe,
        });
    }

    getNextCell(event, {restrictToSelection, currentCell}) {
        const {dataframe, columns, selected_cell} = this.props;
        const e = event;
        const vci = [];

        if (!restrictToSelection) {
            columns.forEach((c, i) => {
                if (!c.hidden) {
                    vci.push(i);
                }
            });
        }

        switch (e.keyCode) {
            case KEY_CODES.ARROW_LEFT:
                return restrictToSelection
                    ? selectionCycle(
                          [currentCell[0], currentCell[1] - 1],
                          selected_cell
                      )
                    : [
                          currentCell[0],
                          R.max(
                              vci[0],
                              vci[R.indexOf(currentCell[1], vci) - 1]
                          ),
                      ];

            case KEY_CODES.ARROW_RIGHT:
            case KEY_CODES.TAB:
                return restrictToSelection
                    ? selectionCycle(
                          [currentCell[0], currentCell[1] + 1],
                          selected_cell
                      )
                    : [
                          currentCell[0],
                          R.min(
                              R.last(vci),
                              vci[R.indexOf(currentCell[1], vci) + 1]
                          ),
                      ];

            case KEY_CODES.ARROW_UP:
                return restrictToSelection
                    ? selectionCycle(
                          [currentCell[0] - 1, currentCell[1]],
                          selected_cell
                      )
                    : [R.max(0, currentCell[0] - 1), currentCell[1]];

            case KEY_CODES.ARROW_DOWN:
            case KEY_CODES.ENTER:
                return restrictToSelection
                    ? selectionCycle(
                          [currentCell[0] + 1, currentCell[1]],
                          selected_cell
                      )
                    : [
                          R.min(dataframe.length - 1, currentCell[0] + 1),
                          currentCell[1],
                      ];

            default:
                throw new Error(
                    `Table.getNextCell: unknown navigation keycode ${e.keyCode}`
                );
        }
    }

    onCopy(e) {
        const {columns, dataframe, selected_cell} = this.props;

        e.preventDefault();
        const el = document.createElement('textarea');
        const selectedRows = R.uniq(R.pluck(0, selected_cell).sort());
        const selectedCols = R.uniq(R.pluck(1, selected_cell).sort());
        const selectedTabularData = R.slice(
            R.head(selectedRows),
            R.last(selectedRows) + 1,
            dataframe
        ).map(row =>
            R.props(selectedCols, R.props(R.pluck('id', columns), row))
        );

        el.value = selectedTabularData
            .map(row => R.values(row).join('\t'))
            .join('\r\n');

        // (Adapted from https://hackernoon.com/copying-text-to-clipboard-with-javascript-df4d4988697f)
        // Make it readonly to be tamper-proof
        el.setAttribute('readonly', '');
        // el.style.position = 'absolute';
        // Move outside the screen to make it invisible
        // el.style.left = '-9999px';
        // Append the <textarea> element to the HTML document
        document.body.appendChild(el);

        // Check if there is any content selected previously
        let selected = false;
        if (document.getSelection().rangeCount > 0) {
            // Store selection if found
            selected = document.getSelection().getRangeAt(0);
        }

        // Select the <textarea> content
        el.select();
        // Copy - only works as a result of a user action (e.g. click events)
        document.execCommand('copy');
        // Remove the <textarea> element
        document.body.removeChild(el);
        // If a selection existed before copying
        if (selected) {
            // Unselect everything on the HTML document
            document.getSelection().removeAllRanges();
            // Restore the original selection
            document.getSelection().addRange(selected);
        }
        // refocus on the table so that onPaste can be fired immediately
        // on the same table
        // note that this requires tabIndex to be set on the <table/>
        this._table.focus();
        return;
    }

    onPaste(e) {
        const {
            columns,
            dataframe,
            editable,
            setProps,
            is_focused,
            active_cell,
        } = this.props;

        if (e && e.clipboardData && !is_focused) {
            const text = e.clipboardData.getData('text/plain');
            if (text) {
                const values = SheetClip.prototype.parse(text);

                let newDataframe = dataframe;
                const newColumns = columns;

                if (values[0].length + active_cell[1] >= columns.length) {
                    for (
                        let i = columns.length;
                        i < values[0].length + active_cell[1];
                        i++
                    ) {
                        newColumns.push({
                            id: `Column ${i + 1}`,
                            type: 'numeric',
                        });
                        newDataframe.forEach(row => (row[`Column ${i}`] = ''));
                    }
                }

                if (values.length + active_cell[0] >= dataframe.length) {
                    const emptyRow = {};
                    columns.forEach(c => (emptyRow[c.name] = ''));
                    newDataframe = R.concat(
                        newDataframe,
                        R.repeat(
                            emptyRow,
                            values.length + active_cell[0] - dataframe.length
                        )
                    );
                }

                values.forEach((row, i) =>
                    row.forEach((cell, j) => {
                        const iOffset = active_cell[0] + i;
                        const jOffset = active_cell[1] + j;
                        // let newDataframe = dataframe;
                        const col = newColumns[jOffset];
                        if (colIsEditable(editable, col)) {
                            newDataframe = R.set(
                                R.lensPath([iOffset, col.id]),
                                cell,
                                newDataframe
                            );
                        }
                    })
                );
                setProps({
                    dataframe: newDataframe,
                    columns: newColumns,
                });
            }
        }
    }

    collectRows(slicedDf, start) {
        const {collapsable, columns, expanded_rows} = this.props;
        const rows = [];
        for (let i = 0; i < slicedDf.length; i++) {
            const row = slicedDf[i];
            rows.push(
                <Row
                    key={start + i}
                    row={row}
                    idx={start + i}
                    {...this.props}
                />
            );
            if (collapsable && R.contains(start + i, expanded_rows)) {
                rows.push(
                    <tr>
                        <td className="expanded-row--empty-cell" />
                        <td colSpan={columns.length} className="expanded-row">
                            <h1>{`More About Row ${start + i}`}</h1>
                        </td>
                    </tr>
                );
            }
        }
        return rows;
    }

    render() {
        const {
            collapsable,
            columns,
            dataframe,
            display_row_count: n,
            display_tail_count: m,
            table_style,
            n_fixed_columns,
            n_fixed_rows,
        } = this.props;

        const table_component = (
            <table
                ref={el => (this._table = el)}
                onPaste={this.onPaste}
                tabIndex={-1}
                style={table_style}
            >
                <Header {...this.props} />

                <tbody>
                    {this.collectRows(dataframe.slice(0, n), 0)}

                    {dataframe.length < n + m ? null : (
                        <tr>
                            {!collapsable ? null : (
                                <td className="expanded-row--empty-cell" />
                            )}
                            <td className="elip" colSpan={columns.length}>
                                {'...'}
                            </td>
                        </tr>
                    )}

                    {dataframe.length < n
                        ? null
                        : this.collectRows(
                              dataframe.slice(
                                  R.max(dataframe.length - m, n),
                                  dataframe.length
                              ),
                              R.max(dataframe.length - m, n)
                          )}
                </tbody>
            </table>
        );

        let tableStyle = null;
        if (n_fixed_columns || n_fixed_rows) {
            tableStyle = computedStyles.scroll.containerDiv(this.props);
        }
        return (
            <div
                className="dash-spreadsheet"
                style={tableStyle}
                onKeyDown={this.handleKeyDown}
            >
                {table_component}
            </div>
        );
    }
}

Table.defaultProps = {
    changed_data: {},
    editable: false,
    active_cell: [0, 0],
    index_name: '',
    types: {},
    merged_styles: {},
    selected_cell: [],
    display_row_count: 20,
    display_tail_count: 5,
    base_styles: {
        numeric: {
            'text-align': 'right',
            'font-family': "'Droid Sans Mono', Courier, monospace",
        },

        string: {
            'text-align': 'left',
        },

        input: {
            padding: 0,
            margin: 0,
            width: '80px',
            border: 'none',
            'font-size': '1rem',
        },

        'input-active': {
            outline: '#7FDBFF auto 3px',
        },

        table: {},

        thead: {},

        th: {},

        td: {},
    },
};

Table.propTypes = {
    active_cell: PropTypes.array,
    collapsable: PropTypes.bool,
    columns: PropTypes.arrayOf(PropTypes.object),
    dataframe_timestamp: PropTypes.any,
    dataframe: PropTypes.arrayOf(PropTypes.object),
    display_row_count: PropTypes.number,
    display_tail_count: PropTypes.number,
    editable: PropTypes.bool,
    end_cell: PropTypes.arrayOf(PropTypes.number),
    expanded_rows: PropTypes.array,
    id: PropTypes.string,
    is_focused: PropTypes.bool,
    merge_duplicate_headers: PropTypes.bool,
    n_fixed_columns: PropTypes.number,
    n_fixed_rows: PropTypes.number,
    selected_cell: PropTypes.arrayOf(PropTypes.number),
    setProps: PropTypes.any,
    table_style: PropTypes.any,
    active_cell: PropTypes.array,
};
