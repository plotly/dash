import React, { PureComponent } from 'react';
import * as R from 'ramda';
import Stylesheet from 'core/Stylesheet';
import {
    KEY_CODES,
    isCtrlMetaKey,
    isCtrlDown,
    isNavKey
} from 'dash-table/utils/unicode';
import { selectionCycle } from 'dash-table/utils/navigation';

import getScrollbarWidth from 'core/browser/scrollbarWidth';
import Logger from 'core/Logger';
import { arrayMap3 } from 'core/math/arrayZipMap';
import { memoizeOne } from 'core/memoizer';
import lexer from 'core/syntax-tree/lexer';

import TableClipboardHelper from 'dash-table/utils/TableClipboardHelper';
import { ControlledTableProps } from 'dash-table/components/Table/props';
import dropdownHelper from 'dash-table/components/dropdownHelper';

import derivedTable from 'dash-table/derived/table';
import derivedTableFragments from 'dash-table/derived/table/fragments';
import derivedTableFragmentStyles from 'dash-table/derived/table/fragmentStyles';
import isEditable from 'dash-table/derived/cell/isEditable';
import { derivedTableStyle } from 'dash-table/derived/style';
import { IStyle } from 'dash-table/derived/style/props';

const sortNumerical = R.sort<number>((a, b) => a - b);

const DEFAULT_STYLE = {
    width: '100%'
};

export default class ControlledTable extends PureComponent<ControlledTableProps> {
    private readonly stylesheet: Stylesheet = new Stylesheet(`#${this.props.id}`);
    private readonly tableFn = derivedTable(() => this.props);
    private readonly tableStyle = derivedTableStyle();

    private calculateTableStyle = memoizeOne((style: Partial<IStyle>) => R.mergeAll(
        this.tableStyle(DEFAULT_STYLE, style)
    ));

    constructor(props: ControlledTableProps) {
        super(props);

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

    private updateUiViewport() {
        const {
            setState,
            uiViewport,
            virtualization
        } = this.props;

        if (!virtualization) {
            return;
        }

        const { r1c1 } = this.refs as { [key: string]: HTMLElement };
        let parent: any = r1c1.parentElement;

        if (uiViewport &&
            uiViewport.scrollLeft === parent.scrollLeft &&
            uiViewport.scrollTop === parent.scrollTop &&
            uiViewport.height === parent.clientHeight &&
            uiViewport.width === parent.clientWidth) {
            return;
        }

        setState({
            uiViewport: {
                scrollLeft: parent.scrollLeft,
                scrollTop: parent.scrollTop,
                height: parent.clientHeight,
                width: parent.clientWidth
            }
        });
    }

    componentDidMount() {
        const {
            active_cell,
            selected_cells,
            setProps
        } = this.props;

        if (selected_cells.length &&
            active_cell.length &&
            !R.contains(active_cell, selected_cells)
        ) {
            setProps({ active_cell: selected_cells[0] });
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

        const {
            setState,
            uiCell,
            virtualization
        } = this.props;

        if (!virtualization) {
            return;
        }

        if (uiCell) {
            return;
        }

        const { r1c1 } = this.refs as { [key: string]: HTMLElement };
        const contentTd = r1c1.querySelector('tr > td:first-of-type');

        if (!contentTd) {
            return;
        }

        const contentThs = r1c1.querySelectorAll('tr th:first-of-type');

        setState({
            uiCell: {
                height: contentTd.clientHeight
            },
            uiHeaders: R.map((th: Element) => ({ height: th.clientHeight }), Array.from(contentThs))
        });
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
        const {
            forcedResizeOnly,
            setState
        } = this.props;

        if (forcedResizeOnly && !force) {
            return;
        }

        if (!force) {
            setState({ forcedResizeOnly: true });
        }

        this.updateStylesheet();

        getScrollbarWidth().then((scrollbarWidth: number) => setState({ scrollbarWidth }));

        const { r0c0, r0c1, r1c0, r1c1 } = this.refs as { [key: string]: HTMLElement };

        // Adjust [fixed columns/fixed rows combo] to fixed rows height
        let trs = r0c1.querySelectorAll('tr');
        Array.from(r0c0.querySelectorAll('tr')).forEach((tr, index) => {
            const tr2 = trs[index];

            tr.style.height = `${tr2.clientHeight}px`;
        });

        // Adjust fixed columns headers to header's height
        let trths = r1c1.querySelectorAll('tr > th:first-of-type');
        Array.from(r1c0.querySelectorAll('tr > th:first-of-type')).forEach((th, index) => {
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
            setProps,
            is_focused
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

        if (!is_focused &&
            isNavKey(e.keyCode)
        ) {
            this.switchCell(e);
        }

        if (
            is_focused &&
            !isNavKey(e.keyCode)
        ) {
            return;
        }

        if (e.keyCode === KEY_CODES.TAB || e.keyCode === KEY_CODES.ENTER) {
            this.switchCell(e);
            return;
        }

        if (
            e.keyCode === KEY_CODES.BACKSPACE ||
            e.keyCode === KEY_CODES.DELETE
        ) {
            this.deleteCell(e);
        }

        return;
    }

    switchCell = (event: any) => {
        const e = event;
        const {
            active_cell,
            columns,
            selected_cells,
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

        const hasSelection = selected_cells.length > 1;
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
                selected_cells: [nextCell],
                active_cell: nextCell
            });
            return;
        }

        // else we are navigating with arrow keys and extending selection
        // with shift.
        let targetCells: any[] = [];
        let removeCells: any[] = [];
        const selectedRows = sortNumerical(R.uniq(R.pluck(0, selected_cells)));
        const selectedCols = sortNumerical(R.uniq(R.pluck(1, selected_cells)));

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
        if (selectingDown && (active_cell as any)[0] > minRow) {
            removeCells = selectedCols.map(col => [minRow, col]);
        } else if (selectingDown && maxRow !== viewport.data.length - 1) {
            // Otherwise if we are selecting down select the next row if possible.
            targetCells = selectedCols.map(col => [maxRow + 1, col]);
        } else if (selectingUp && (active_cell as any)[0] < maxRow) {
            // If there are selections below the active cell and we are selecting
            // up remove lower row.
            removeCells = selectedCols.map(col => [maxRow, col]);
        } else if (selectingUp && minRow > 0) {
            // Otherwise if we are selecting up select next row if possible.
            targetCells = selectedCols.map(col => [minRow - 1, col]);
        } else if (selectingLeft && (active_cell as any)[1] < maxCol) {
            // If there are selections to the right of the active cell and
            // we are selecting left, move the right side closer to active_cell
            removeCells = selectedRows.map(row => [row, maxCol]);
        } else if (selectingLeft && minCol > 0) {
            // Otherwise increase the selection left if possible
            targetCells = selectedRows.map(row => [row, minCol - 1]);
        } else if (selectingRight && (active_cell as any)[1] > minCol) {
            // If there are selections to the left of the active cell and
            // we are selecting right, move the left side closer to active_cell
            removeCells = selectedRows.map(row => [row, minCol]);
        } else if (selectingRight && maxCol + 1 <= columns.length - 1) {
            // Otherwise move selection right if possible
            targetCells = selectedRows.map(row => [row, maxCol + 1]);
        }

        const newSelectedCell = R.without(
            removeCells,
            R.uniq(R.concat(targetCells, selected_cells))
        );
        setProps({
            is_focused: false,
            selected_cells: newSelectedCell
        });
    }

    deleteCell = (event: any) => {
        const {
            columns,
            data,
            editable,
            selected_cells,
            setProps,
            viewport
        } = this.props;

        event.preventDefault();

        let newData = data;

        const realCells: [number, number][] = R.map(
            cell => [viewport.indices[cell[0]], cell[1]] as [number, number],
            selected_cells
        );

        realCells.forEach(cell => {
            if (isEditable(editable, columns[cell[1]].editable)) {
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
        const { columns, selected_cells, viewport } = this.props;

        const e = event;

        switch (e.keyCode) {
            case KEY_CODES.ARROW_LEFT:
                return restrictToSelection
                    ? selectionCycle(
                        [currentCell[0], currentCell[1] - 1],
                        selected_cells
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
                        selected_cells
                    )
                    : [
                        currentCell[0],
                        R.min(columns.length - 1, currentCell[1] + 1)
                    ];

            case KEY_CODES.ARROW_UP:
                return restrictToSelection
                    ? selectionCycle(
                        [currentCell[0] - 1, currentCell[1]],
                        selected_cells
                    )
                    : [R.max(0, currentCell[0] - 1), currentCell[1]];

            case KEY_CODES.ARROW_DOWN:
            case KEY_CODES.ENTER:
                return restrictToSelection
                    ? selectionCycle(
                        [currentCell[0] + 1, currentCell[1]],
                        selected_cells
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
            selected_cells,
            viewport
        } = this.props;

        TableClipboardHelper.toClipboard(e, selected_cells, columns, viewport.data);
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

        this.updateUiViewport();

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
            Array.from(r1c1.querySelectorAll('tr:first-of-type td, tr:first-of-type th')).forEach((td, index) => {
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
            Array.from(r1c0.querySelectorAll('tr:first-of-type td, tr:first-of-type th')).forEach((td, index) => {
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

        this.updateUiViewport();
        this.handleDropdown();
    }

    render() {
        const {
            id,
            content_style,
            n_fixed_columns,
            n_fixed_rows,
            scrollbarWidth,
            style_as_list_view,
            style_table,
            uiCell,
            uiHeaders,
            uiViewport,
            viewport,
            virtualized,
            virtualization
        } = this.props;

        const containerClasses = [
            'dash-spreadsheet',
            'dash-spreadsheet-container',
            ...(virtualization ? ['dash-virtualized'] : []),
            ...(n_fixed_rows ? ['dash-freeze-top'] : []),
            ...(n_fixed_columns ? ['dash-freeze-left'] : []),
            ...(style_as_list_view ? ['dash-list-view'] : []),
            [`dash-${content_style}`]
        ];

        const classes = [
            'dash-spreadsheet',
            'dash-spreadsheet-inner',
            ...(virtualization ? ['dash-virtualized'] : []),
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
        const grid = derivedTableFragments(
            n_fixed_columns,
            n_fixed_rows,
            rawTable,
            virtualized.offset.rows
        );

        const tableStyle = this.calculateTableStyle(style_table);
        const gridStyle = derivedTableFragmentStyles(
            virtualization,
            uiCell,
            uiHeaders,
            uiViewport,
            viewport,
            virtualized.padding.rows,
            scrollbarWidth
        );

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
                    >
                        {arrayMap3(row, gridStyle[rowIndex], fragmentClasses[rowIndex], (g, s, c, columnIndex) => (<div
                            style={s.fragment}
                            key={columnIndex}
                            ref={`r${rowIndex}c${columnIndex}`}
                            className={`cell cell-${rowIndex}-${columnIndex} ${c}`}
                        >
                            {g ? React.cloneElement(g, { style: s.cell }) : g}
                        </div>))}
                    </div>))}
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
