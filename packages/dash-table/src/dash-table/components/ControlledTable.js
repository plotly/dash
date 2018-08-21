import React, { Component } from 'react';
import * as R from 'ramda';
import SheetClip from 'sheetclip';
import Stylesheet from 'core/Stylesheet';
import { colIsEditable } from 'dash-table/components/derivedState';
import {
    KEY_CODES,
    isCtrlMetaKey,
    isCtrlDown,
    isMetaKey,
    isNavKey,
} from 'dash-table/utils/unicode';
import { selectionCycle } from 'dash-table/utils/navigation';

import { propTypes } from 'dash-table/components/Table';

import HeaderFactory from 'dash-table/components/HeaderFactory';
import RowFactory from 'dash-table/components/RowFactory';
import { DEFAULT_CELL_WIDTH } from 'dash-table/components/Row';

const sortNumerical = R.sort((a, b) => a - b);

export default class ControlledTable extends Component {
    constructor(props) {
        super(props);

        this.handleKeyDown = this.handleKeyDown.bind(this);
        this.onPaste = this.onPaste.bind(this);
        this.handleClickOutside = this.handleClickOutside.bind(this);
        this.handlePaste = this.handlePaste.bind(this);
        this.getDomElement = this.getDomElement.bind(this);
        this.onContainerScroll = this.onContainerScroll.bind(this);

        this.loadNext = this.loadNext.bind(this);
        this.loadPrevious = this.loadPrevious.bind(this);

        this.listeners = {};

        this.stylesheet = new Stylesheet(`#${props.id}`);
    }

    componentDidMount() {
        if (
            this.props.selected_cell.length &&
            !R.contains(this.props.active_cell, this.props.selected_cell)
        ) {
            this.props.setProps({ active_cell: this.props.selected_cell[0] });
        }
        document.addEventListener('mousedown', this.handleClickOutside);

        // Fallback method for paste handling in Chrome
        // when no input element has focused inside the table
        document.addEventListener('paste', this.handlePaste);
    }

    componentWillUnmount() {
        document.removeEventListener('mousedown', this.handleClickOutside);
        document.removeEventListener('paste', this.handlePaste);
    }

    handleClickOutside(event) {
        if (this.getDomElement() && !this.getDomElement().contains(event.target)) {
            this.props.setProps({ is_focused: false });
        }
    }

    handlePaste(event) {
        // no need to check for target as this will only be called if
        // a child fails to handle the paste event (e.g table, table input)
        // make sure the active element is in the scope of the component
        const el = this.getDomElement();
        if (el && el.contains(document.activeElement)) {
            this.onPaste(event);
        }
    }

    getDomElement() {
        // this.ref is unreliable, so just use query selector
        return document.getElementById(this.props.id);
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
            setProps({ is_focused: false });
            return;
        }

        if (
            e.keyCode === KEY_CODES.ENTER &&
            !is_focused &&
            colIsEditable(editable, columns[active_cell[1]])
        ) {
            setProps({ is_focused: true });
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
            setProps({ is_focused: true });
        }

        return;
    }

    switchCell(event) {
        const e = event;
        const {
            active_cell,
            columns,
            selected_cell,
            setProps,
            virtualizer
        } = this.props;

        const dataframe = virtualizer.dataframe;

        // This is mostly to prevent TABing also triggering native HTML tab
        // navigation. If the preventDefault is too greedy here we must
        // continue to use it for at least the case we are navigating with
        // TAB
        event.preventDefault();

        // If we are moving yank focus away from whatever input may still have
        // focus.
        // TODO There is a better way to handle native focus being out of sync
        // with the "is_focused" prop. We should find the better way.
        this.getDomElement().focus();

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
        const selectedRows = sortNumerical(R.uniq(R.pluck(0, selected_cell)));
        const selectedCols = sortNumerical(R.uniq(R.pluck(1, selected_cell)));

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
            editable,
            selected_cell,
            setProps,
            virtualizer
        } = this.props;

        const dataframe = virtualizer.dataframe;

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

    getNextCell(event, { restrictToSelection, currentCell }) {
        const { columns, selected_cell, virtualizer } = this.props;
        const dataframe = virtualizer.dataframe;

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
        const { columns, selected_cell, virtualizer } = this.props;
        const dataframe = virtualizer.dataframe;

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
        this.getDomElement().focus();
        return;
    }

    onPaste(e) {
        const {
            columns,
            editable,
            setProps,
            is_focused,
            active_cell,
            dataframe
        } = this.props;
        if (e && e.clipboardData && !is_focused) {
            const text = e.clipboardData.getData('text/plain');
            console.warn('clipboard data: ', text);
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
                    columns.forEach(c => (emptyRow[c.id] = ''));
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

    get displayPagination() {
        const {
            dataframe,
            navigation,
            virtualization,
            virtualization_settings
        } = this.props;

        return navigation === 'page' &&
            (
                (virtualization === 'fe' && virtualization_settings.page_size < dataframe.length) ||
                virtualization === 'be'
            );
    }

    loadNext() {
        const { virtualizer } = this.props;

        virtualizer.loadNext();
    }

    loadPrevious() {
        const { virtualizer } = this.props;

        virtualizer.loadPrevious();
    }

    componentWillUpdate() {
        const { table_style } = this.props;

        R.forEach(({ selector, rule }) => {
            this.stylesheet.setRule(selector, rule);
        }, table_style);
    }

    componentDidUpdate() {
        const { n_fixed_columns = 0, n_fixed_rows = 0 } = this.props;
        if (!n_fixed_columns && !n_fixed_rows) {
            return;
        }

        const { container, frozenTop } = this.refs;

        if (n_fixed_columns > 0) {
            // Find the height of the <tr /> of the first <td /> and <th />
            // Assume that these table rows are representative in style with the rest of the table
            // Use them to force the height of the fixed cells; base styling vs. rendering can be off

            const fixedTd = container.querySelector(`td.frozen-left`);
            const tdHeight = parseInt(getComputedStyle(fixedTd.parentElement).height, 10);

            const fixedTh = container.querySelector(`th.frozen-left`);
            const thHeight = parseInt(getComputedStyle(fixedTh.parentElement).height, 10);

            this.stylesheet.setRule(`td.frozen-left`, `height: ${tdHeight}px;`)
            this.stylesheet.setRule(`th.frozen-left`, `height: ${thHeight}px;`)
        }

        let xOffset = 0;
        R.range(0, n_fixed_columns).forEach(index => {
            this.stylesheet.setRule(`.frozen-left-${index}`, `margin-left: ${xOffset}px;`);

            const fixedCell = container.querySelector(`td.frozen-left-${index}`);
            if (fixedCell) {
                xOffset += (fixedCell.clientWidth || parseInt(getComputedStyle(fixedCell).width, 10));
            }
        });
        this.stylesheet.setRule(`.dash-spreadsheet`, `padding-left: ${xOffset}px; padding-top: ${frozenTop ? frozenTop.clientHeight : 0}px;`);

        R.forEach(
            cell => { cell.style.height = cell.parentElement.clientHeight },
            container.querySelectorAll('tr th.frozen-left')
        );
    }

    onContainerScroll(ev) {
        const { n_fixed_columns } = this.props;
        if (!n_fixed_columns) {
            return;
        }

        const { spreadsheet } = this.refs;
        if (ev.target !== spreadsheet) {
            return;
        }

        this.stylesheet.setRule(`.frozen-left`, `margin-top: ${-ev.target.scrollTop}px;`);
    }

    render() {
        const {
            id,
            columns,
            n_fixed_columns,
            n_fixed_rows,
            row_deletable,
            row_selectable
        } = this.props;

        const rows = [
            ...HeaderFactory.createHeaders(this.props),
            ...RowFactory.createRows(this.props)
        ];

        const fixedRows = rows.splice(0, n_fixed_rows);
        const hasFixedRows = fixedRows.length !== 0;

        let typeIndex = 0;
        if (row_deletable) {
            this.stylesheet.setRule(
                `.dash-spreadsheet td:nth-of-type(${++typeIndex})`,
                `width: 30px; max-width: 30px; min-width: 30px;`
            );
            this.stylesheet.setRule(
                `.dash-spreadsheet th:nth-of-type(${typeIndex})`,
                `width: 30px; max-width: 30px; min-width: 30px;`
            );
        }

        if (row_selectable) {
            this.stylesheet.setRule(
                `.dash-spreadsheet td:nth-of-type(${++typeIndex})`,
                `width: 30px; max-width: 30px; min-width: 30px;`
            );
            this.stylesheet.setRule(
                `.dash-spreadsheet th:nth-of-type(${typeIndex})`,
                `width: 30px; max-width: 30px; min-width: 30px;`
            );
        }

        R.forEach(column => {
            const width = Stylesheet.unit(column.width || DEFAULT_CELL_WIDTH, 'px');

            this.stylesheet.setRule(
                `.dash-spreadsheet td:nth-of-type(${++typeIndex})`,
                `width: ${width}; max-width: ${width}; min-width: ${width};`
            );
            this.stylesheet.setRule(
                `.dash-spreadsheet th:nth-of-type(${typeIndex})`,
                `width: ${width}; max-width: ${width}; min-width: ${width};`
            );
        }, columns)


        const table_component = (
            <div
                className={[
                    'dash-spreadsheet',
                    ...(hasFixedRows ? ['freeze-top'] : []),
                    ...(n_fixed_columns ? ['freeze-left'] : [])
                ].join(' ')}
                onKeyDown={this.handleKeyDown}
                onScroll={this.onContainerScroll}
                key={`${id}-table-container`}
                ref='spreadsheet'
            >
                <table
                    id={id}
                    key={`${id}-table`}
                    onPaste={this.onPaste}
                    tabIndex={-1}
                >
                    {hasFixedRows ? <tbody
                        className={'frozen-top'}
                        ref='frozenTop'
                    >
                        {fixedRows}
                    </tbody> : null}

                    {<tbody>
                        {rows}
                    </tbody>}
                </table>
            </div>
        );

        return (
            <div id={id}>
                <div className={[
                    'dash-spreadsheet-clipper',
                    ...(hasFixedRows ? ['freeze-top'] : []),
                    ...(n_fixed_columns ? ['freeze-left'] : [])
                ].join(' ')}>
                    <div
                        className='dash-spreadsheet-container'
                        ref='container'
                    >
                        {table_component}
                    </div>
                </div>
                {!this.displayPagination ? null : (
                    <div>
                        <button className='previous-page' onClick={this.loadPrevious}>Previous</button>
                        <button className='next-page' onClick={this.loadNext}>Next</button>
                    </div>
                )}
            </div>
        );
    }
}

ControlledTable.propTypes = propTypes;