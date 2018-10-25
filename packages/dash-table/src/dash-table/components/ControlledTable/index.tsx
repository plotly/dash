import React, { PureComponent } from 'react';
import * as R from 'ramda';
import Stylesheet from 'core/Stylesheet';
import {
    KEY_CODES,
    isCtrlMetaKey,
    isCtrlDown,
    isMetaKey,
    isNavKey
} from 'dash-table/utils/unicode';
import { selectionCycle } from 'dash-table/utils/navigation';

import Logger from 'core/Logger';
import { memoizeOne } from 'core/memoizer';
import lexer from 'core/syntax-tree/lexer';

import TableClipboardHelper from 'dash-table/utils/TableClipboardHelper';
import { ControlledTableProps } from 'dash-table/components/Table/props';
import dropdownHelper from 'dash-table/components/dropdownHelper';

import derivedTable from 'dash-table/derived/table';
import derivedTableFragments from 'dash-table/derived/table/fragments';
import isEditable from 'dash-table/derived/cell/isEditable';
import { derivedTableStyle } from 'dash-table/derived/style';

const sortNumerical = R.sort<number>((a, b) => a - b);

interface IState {
    forcedResizeOnly: boolean;
}

export default class ControlledTable extends PureComponent<ControlledTableProps, IState> {
    private readonly stylesheet: Stylesheet;
    private readonly tableFn: () => JSX.Element[][];
    private readonly tableStyle = derivedTableStyle();

    constructor(props: ControlledTableProps) {
        super(props);

        this.state = {
            forcedResizeOnly: false
        };

        this.stylesheet = new Stylesheet(`#${props.id}`);
        this.tableFn = derivedTable(() => this.props);
        this.updateStylesheet();
    }

    getLexerResult = memoizeOne(lexer);

    get lexerResult() {
        const { filtering_settings } = this.props;

        return this.getLexerResult(filtering_settings);
    }

    private updateStylesheet() {
        const { css } = this.props;

        R.forEach(({ selector, rule }) => {
            this.stylesheet.setRule(selector, rule);
        }, css);
    }

    componentDidMount() {
        if (
            this.props.selected_cell.length &&
            !R.contains(this.props.active_cell, this.props.selected_cell)
        ) {
            this.props.setProps({ active_cell: this.props.selected_cell[0] });
        }

        this.applyStyle();
        this.handleResize();
    }

    componentWillMount() {
        // Fallback method for paste handling in Chrome
        // when no input element has focused inside the table
        window.addEventListener('resize', this.forceHandleResize);
        document.addEventListener('paste', this.handlePaste);
        document.addEventListener('mousedown', this.handleClickOutside);
    }

    componentWillUnmount() {
        window.removeEventListener('resize', this.forceHandleResize);
        document.removeEventListener('mousedown', this.handleClickOutside);
        document.removeEventListener('paste', this.handlePaste);
    }

    componentWillUpdate() {
        this.updateStylesheet();
    }

    componentDidUpdate() {
        this.applyStyle();
        this.handleResize();
        this.handleDropdown();
    }

    handleClickOutside = (event: any) => {
        const $el = this.$el;

        if ($el &&
            !$el.contains(event.target as Node) &&
            /*
             * setProps is expensive, it causes excessive re-rendering in Dash.
             * so, only call when the table isn't already focussed, otherwise
             * the app will excessively re-render on _every click on the page_
             */
            this.props.is_focused) {
            this.props.setProps({ is_focused: false });
        }
    }

    handlePaste = (event: any) => {
        // no need to check for target as this will only be called if
        // a child fails to handle the paste event (e.g table, table input)
        // make sure the active element is in the scope of the component
        const $el = this.$el;
        if ($el && $el.contains(document.activeElement)) {
            this.onPaste(event);
        }
    }

    forceHandleResize = () => this.handleResize(true);

    handleResize = (force: boolean = false) => {
        if (this.state.forcedResizeOnly && !force) {
            return;
        }

        if (!force) {
            this.setState({ forcedResizeOnly: true });
        }

        this.updateStylesheet();

        const { r0c0, r0c1, r1c0, r1c1 } = this.refs as { [key: string]: HTMLElement };

        // Adjust [fixed columns/fixed rows combo] to fixed rows height
        let trs = r0c1.querySelectorAll('tr');
        r0c0.querySelectorAll('tr').forEach((tr, index) => {
            const tr2 = trs[index];

            tr.style.height = `${tr2.clientHeight}px`;
        });

        // Adjust fixed columns headers to header's height
        let trths = r1c1.querySelectorAll('tr > th:first-of-type');
        r1c0.querySelectorAll('tr > th:first-of-type').forEach((th, index) => {
            const tr2 = trths[index].parentElement as HTMLElement;
            const tr = th.parentElement as HTMLElement;

            tr.style.height = getComputedStyle(tr2).height;
        });

        // Adjust fixed columns data to data height
        const contentTd = r1c1.querySelector('tr > td:first-of-type');
        if (contentTd) {
            const contentTr = contentTd.parentElement as HTMLElement;

            this.stylesheet.setRule('.dash-fixed-column tr', `height: ${getComputedStyle(contentTr).height};`);
        }
    }

    get $el() {
        return document.getElementById(this.props.id) as HTMLElement;
    }

    handleKeyDown = (e: any) => {
        const {
            active_cell,
            columns,
            setProps,
            is_focused,
            editable
        } = this.props;

        Logger.trace(`handleKeyDown: ${e.key}`);

        // if this is the initial CtrlMeta keydown with no modifiers then pass
        if (isCtrlMetaKey(e.keyCode)) {
            return;
        }

        const ctrlDown = isCtrlDown(e);

        if (ctrlDown && e.keyCode === KEY_CODES.V) {
            /*#if TEST_COPY_PASTE*/
            this.onPaste({} as any);
            e.preventDefault();
            /*#endif*/
            return;
        }

        if (e.keyCode === KEY_CODES.C && ctrlDown && !is_focused) {
            /*#if TEST_COPY_PASTE*/
            this.onCopy(e as any);
            e.preventDefault();
            /*#endif*/
            return;
        }

        if (e.keyCode === KEY_CODES.ESCAPE) {
            setProps({ is_focused: false });
            return;
        }

        if (
            e.keyCode === KEY_CODES.ENTER &&
            !is_focused &&
            isEditable(editable, columns[active_cell[1]])
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
        } else if (
            // if we have any non-meta key enter editable mode

            !this.props.is_focused &&
            isEditable(editable, columns[active_cell[1]]) &&
            !isMetaKey(e.keyCode)
        ) {
            setProps({ is_focused: true });
        }

        return;
    }

    switchCell = (event: any) => {
        const e = event;
        const {
            active_cell,
            columns,
            selected_cell,
            setProps,
            viewport
        } = this.props;

        // This is mostly to prevent TABing also triggering native HTML tab
        // navigation. If the preventDefault is too greedy here we must
        // continue to use it for at least the case we are navigating with
        // TAB
        event.preventDefault();

        // If we are moving yank focus away from whatever input may still have
        // focus.
        // TODO There is a better way to handle native focus being out of sync
        // with the "is_focused" prop. We should find the better way.
        this.$el.focus();

        const hasSelection = selected_cell.length > 1;
        const isEnterOrTab =
            e.keyCode === KEY_CODES.ENTER || e.keyCode === KEY_CODES.TAB;

        // If we have a multi-cell selection and are using ENTER or TAB
        // move active cell within the selection context.
        if (hasSelection && isEnterOrTab) {
            const nextCell = this.getNextCell(e, {
                currentCell: active_cell,
                restrictToSelection: true
            });
            setProps({
                is_focused: false,
                active_cell: nextCell
            });
            return;
        } else if (!e.shiftKey) {
            // If we are not extending selection with shift and are
            // moving with navigation keys cancel selection and move.

            const nextCell = this.getNextCell(e, {
                currentCell: active_cell,
                restrictToSelection: false
            });
            setProps({
                is_focused: false,
                selected_cell: [nextCell],
                active_cell: nextCell
            });
            return;
        }

        // else we are navigating with arrow keys and extending selection
        // with shift.
        let targetCells: any[] = [];
        let removeCells: any[] = [];
        const selectedRows = sortNumerical(R.uniq(R.pluck(0, selected_cell)));
        const selectedCols = sortNumerical(R.uniq(R.pluck(1, selected_cell)));

        const minRow = selectedRows[0];
        const minCol = selectedCols[0];
        const maxRow = selectedRows[selectedRows.length - 1];
        const maxCol = selectedCols[selectedCols.length - 1];

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
        } else if (selectingDown && maxRow !== viewport.data.length - 1) {
            // Otherwise if we are selecting down select the next row if possible.
            targetCells = selectedCols.map(col => [maxRow + 1, col]);
        } else if (selectingUp && active_cell[0] < maxRow) {
            // If there are selections below the active cell and we are selecting
            // up remove lower row.
            removeCells = selectedCols.map(col => [maxRow, col]);
        } else if (selectingUp && minRow > 0) {
            // Otherwise if we are selecting up select next row if possible.
            targetCells = selectedCols.map(col => [minRow - 1, col]);
        } else if (selectingLeft && active_cell[1] < maxCol) {
            // If there are selections to the right of the active cell and
            // we are selecting left, move the right side closer to active_cell
            removeCells = selectedRows.map(row => [row, maxCol]);
        } else if (selectingLeft && minCol > 0) {
            // Otherwise increase the selection left if possible
            targetCells = selectedRows.map(row => [row, minCol - 1]);
        } else if (selectingRight && active_cell[1] > minCol) {
            // If there are selections to the left of the active cell and
            // we are selecting right, move the left side closer to active_cell
            removeCells = selectedRows.map(row => [row, minCol]);
        } else if (selectingRight && maxCol + 1 <= columns.length - 1) {
            // Otherwise move selection right if possible
            targetCells = selectedRows.map(row => [row, maxCol + 1]);
        }

        const newSelectedCell = R.without(
            removeCells,
            R.uniq(R.concat(targetCells, selected_cell))
        );
        setProps({
            is_focused: false,
            selected_cell: newSelectedCell
        });
    }

    deleteCell = (event: any) => {
        const {
            columns,
            data,
            editable,
            selected_cell,
            setProps,
            viewport
        } = this.props;

        event.preventDefault();

        let newData = data;

        const realCells: [number, number][] = R.map(
            cell => [viewport.indices[cell[0]], cell[1]] as [number, number],
            selected_cell
        );

        realCells.forEach(cell => {
            if (isEditable(editable, columns[cell[1]])) {
                newData = R.set(
                    R.lensPath([cell[0], columns[cell[1]].id]),
                    '',
                    newData
                );
            }
        });

        setProps({
            data: newData
        });
    }

    getNextCell = (event: any, { restrictToSelection, currentCell }: any) => {
        const { columns, selected_cell, viewport } = this.props;

        const e = event;

        switch (e.keyCode) {
            case KEY_CODES.ARROW_LEFT:
                return restrictToSelection
                    ? selectionCycle(
                        [currentCell[0], currentCell[1] - 1],
                        selected_cell
                    )
                    : [
                        currentCell[0],
                        R.max(0, currentCell[1] - 1)
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
                        R.min(columns.length - 1, currentCell[1] + 1)
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
                        R.min(viewport.data.length - 1, currentCell[0] + 1),
                        currentCell[1]
                    ];

            default:
                throw new Error(
                    `Table.getNextCell: unknown navigation keycode ${e.keyCode}`
                );
        }
    }

    onCopy = (e: any) => {
        const {
            columns,
            selected_cell,
            viewport
        } = this.props;

        TableClipboardHelper.toClipboard(e, selected_cell, columns, viewport.data);
        this.$el.focus();
    }

    onPaste = (e: any) => {
        const {
            active_cell,
            columns,
            data,
            editable,
            filtering_settings,
            setProps,
            sorting_settings,
            viewport
        } = this.props;

        if (!editable) {
            return;
        }

        const result = TableClipboardHelper.fromClipboard(
            e,
            active_cell,
            viewport.indices,
            columns,
            data,
            true,
            !sorting_settings.length || !filtering_settings.length
        );

        if (result) {
            setProps(result);
        }
    }

    get displayPagination() {
        const {
            data,
            navigation,
            pagination_mode,
            pagination_settings
        } = this.props;

        return navigation === 'page' &&
            (
                (pagination_mode === 'fe' && pagination_settings.page_size < data.length) ||
                pagination_mode === 'be'
            );
    }

    loadNext = () => {
        const { paginator } = this.props;

        paginator.loadNext();
    }

    loadPrevious = () => {
        const { paginator } = this.props;

        paginator.loadPrevious();
    }

    applyStyle = () => {
        const {
            n_fixed_columns,
            n_fixed_rows,
            row_deletable,
            row_selectable
        } = this.props;

        const { r1c0, r1c1 } = this.refs as { [key: string]: HTMLElement };

        if (row_deletable) {
            this.stylesheet.setRule(
                `.dash-spreadsheet-inner td.dash-delete-cell`,
                `width: 30px; max-width: 30px; min-width: 30px;`
            );
            this.stylesheet.setRule(
                `.dash-spreadsheet-inner th.dash-delete-header`,
                `width: 30px; max-width: 30px; min-width: 30px;`
            );
        }

        if (row_selectable) {
            this.stylesheet.setRule(
                `.dash-spreadsheet-inner td.dash-select-cell`,
                `width: 30px; max-width: 30px; min-width: 30px;`
            );
            this.stylesheet.setRule(
                `.dash-spreadsheet-inner th.dash-select-header`,
                `width: 30px; max-width: 30px; min-width: 30px;`
            );
        }

        // Adjust the width of the fixed row header
        if (n_fixed_rows) {
            r1c1.querySelectorAll('tr:first-of-type td, tr:first-of-type th').forEach((td, index) => {
                const style = getComputedStyle(td);
                const width = style.width;

                this.stylesheet.setRule(
                    `.dash-fixed-row:not(.dash-fixed-column) th:nth-of-type(${index + 1})`,
                    `width: ${width}; min-width: ${width}; max-width: ${width};`
                );
            });
        }

        // Adjust the width of the fixed row / fixed columns header
        if (n_fixed_columns && n_fixed_rows) {
            r1c0.querySelectorAll('tr:first-of-type td, tr:first-of-type th').forEach((td, index) => {
                const style = getComputedStyle(td);
                const width = style.width;

                this.stylesheet.setRule(
                    `.dash-fixed-column.dash-fixed-row th:nth-of-type(${index + 1})`,
                    `width: ${width}; min-width: ${width}; max-width: ${width};`
                );
            });
        }
    }

    handleDropdown = () => {
        const { r1c1 } = this.refs as { [key: string]: HTMLElement };

        dropdownHelper(r1c1.querySelector('.Select-menu-outer'));
    }

    onScroll = (ev: any) => {
        const { r0c1 } = this.refs as { [key: string]: HTMLElement };

        Logger.trace(`ControlledTable fragment scrolled to (left,top)=(${ev.target.scrollLeft},${ev.target.scrollTop})`);
        r0c1.style.marginLeft = `${-ev.target.scrollLeft}px`;

        this.handleDropdown();
    }

    render() {
        const {
            id,
            content_style,
            n_fixed_columns,
            n_fixed_rows,
            style_as_list_view,
            style_table
        } = this.props;

        const classes = [
            'dash-spreadsheet-inner',
            'dash-spreadsheet',
            ...(n_fixed_rows ? ['dash-freeze-top'] : []),
            ...(n_fixed_columns ? ['dash-freeze-left'] : []),
            ...(style_as_list_view ? ['dash-list-view'] : []),
            [`dash-${content_style}`]
        ];

        const containerClasses = [
            'dash-spreadsheet',
            'dash-spreadsheet-container',
            ...(n_fixed_rows ? ['dash-freeze-top'] : []),
            ...(n_fixed_columns ? ['dash-freeze-left'] : []),
            ...(style_as_list_view ? ['dash-list-view'] : []),
            [`dash-${content_style}`]
        ];

        const fragmentClasses = [
            [
                n_fixed_rows && n_fixed_columns ? 'dash-fixed-row dash-fixed-column' : '',
                n_fixed_rows ? 'dash-fixed-row' : ''
            ],
            [
                n_fixed_columns ? 'dash-fixed-column' : '',
                'dash-fixed-content'
            ]
        ];

        const rawTable = this.tableFn();
        const grid = derivedTableFragments(n_fixed_columns, n_fixed_rows, rawTable);

        const tableStyle = this.tableStyle(style_table);

        return (<div
            id={id}
            onCopy={this.onCopy}
            onKeyDown={this.handleKeyDown}
            onPaste={this.onPaste}
        >
            <div className={containerClasses.join(' ')} style={tableStyle}>
                <div className={classes.join(' ')} style={tableStyle}>
                    {grid.map((row, rowIndex) => (<div
                        key={`r${rowIndex}`}
                        ref={`r${rowIndex}`}
                        className={`row row-${rowIndex}`}
                        onScroll={this.onScroll}
                    >{row.map((cell, columnIndex) => (<div
                        key={columnIndex}
                        ref={`r${rowIndex}c${columnIndex}`}
                        className={`cell cell-${rowIndex}-${columnIndex} ${fragmentClasses[rowIndex][columnIndex]}`}
                    >{cell}</div>))
                        }</div>))}
                </div>
            </div>
            {!this.displayPagination ? null : (
                <div>
                    <button className='previous-page' onClick={this.loadPrevious}>Previous</button>
                    <button className='next-page' onClick={this.loadNext}>Next</button>
                </div>
            )}
        </div>);
    }
}
