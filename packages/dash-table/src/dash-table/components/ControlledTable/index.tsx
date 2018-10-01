import React, { Component } from 'react';
import * as R from 'ramda';
import Stylesheet from 'core/Stylesheet';
import { colIsEditable } from 'dash-table/components/derivedState';
import {
    KEY_CODES,
    isCtrlMetaKey,
    isCtrlDown,
    isMetaKey,
    isNavKey
} from 'dash-table/utils/unicode';
import { selectionCycle } from 'dash-table/utils/navigation';

import HeaderCellFactory, { DEFAULT_CELL_WIDTH } from 'dash-table/components/HeaderFactory';
import Logger from 'core/Logger';
import { memoizeOne } from 'core/memoizer';
import lexer from 'core/syntax-tree/lexer';

import TableClipboardHelper from 'dash-table/utils/TableClipboardHelper';
import CellFactory from 'dash-table/components/CellFactory';
import { ControlledTableProps, Columns, RowSelection } from 'dash-table/components/Table/props';
import dropdownHelper from 'dash-table/components/dropdownHelper';
import HeaderFilterFactory from 'dash-table/components/FilterFactory';

const sortNumerical = R.sort<number>((a, b) => a - b);

interface IAccumulator {
    cells: number;
    count: number;
}

export default class ControlledTable extends Component<ControlledTableProps> {
    private stylesheet: Stylesheet;
    private cellFactory: CellFactory;
    private filterFactory: HeaderFilterFactory;

    constructor(props: ControlledTableProps) {
        super(props);

        this.cellFactory = new CellFactory(() => this.props);
        this.filterFactory = new HeaderFilterFactory(() => {
            const { row_deletable, row_selectable } = this.props;

            const offset =
                (row_deletable ? 1 : 0) +
                (row_selectable ? 1 : 0);

            return {
                columns: this.props.columns,
                filtering: this.props.filtering,
                filtering_settings: this.props.filtering_settings,
                filtering_type: this.props.filtering_type,
                id: this.props.id,
                offset,
                setFilter: this.handleSetFilter
            };
        });
        this.stylesheet = new Stylesheet(`#${props.id}`);
    }

    getLexerResult = memoizeOne(lexer);

    get lexerResult() {
        const { filtering_settings } = this.props;

        return this.getLexerResult(filtering_settings);
    }

    componentDidMount() {
        if (
            this.props.selected_cell.length &&
            !R.contains(this.props.active_cell, this.props.selected_cell)
        ) {
            this.props.setProps({ active_cell: this.props.selected_cell[0] });
        }

        // Fallback method for paste handling in Chrome
        // when no input element has focused inside the table
        window.addEventListener('resize', this.handleResize);
        document.addEventListener('paste', this.handlePaste);
        document.addEventListener('mousedown', this.handleClickOutside);
    }

    componentWillUnmount() {
        window.removeEventListener('resize', this.handleResize);
        document.removeEventListener('mousedown', this.handleClickOutside);
        document.removeEventListener('paste', this.handlePaste);
    }

    componentWillUpdate() {
        const { table_style } = this.props;

        R.forEach(({ selector, rule }) => {
            this.stylesheet.setRule(selector, rule);
        }, table_style);
    }

    componentDidUpdate() {
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

    handleResize = () => {
        const { r0c0, r0c1, r1c0, r1c1 } = this.refs as { [key: string]: HTMLElement };

        // Adjust [fixed columns/fixed rows combo] to fixed rows height
        let trs = r0c1.querySelectorAll('tr');
        r0c0.querySelectorAll('tr').forEach((tr, index) => {
            const tr2 = trs[index];

            tr.style.height = getComputedStyle(tr2).height;
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

            this.stylesheet.setRule('.cell-1-0 tr', `height: ${getComputedStyle(contentTr).height}`);
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
        } else if (
            // if we have any non-meta key enter editable mode

            !this.props.is_focused &&
            colIsEditable(editable, columns[active_cell[1]]) &&
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
            row_deletable,
            row_selectable,
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

        // visible col indices
        const columnIndexOffset =
            (row_deletable ? 1 : 0) +
            (row_selectable ? 1 : 0);

        const vci: any[] = [];
        columns.forEach((c, i) => {
            if (!c.hidden) {
                vci.push(i + columnIndexOffset);
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
        } else if (selectingDown && maxRow !== dataframe.length - 1) {
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
        } else if (selectingRight && maxCol + 1 <= R.last(vci)) {
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
            dataframe,
            editable,
            row_deletable,
            row_selectable,
            selected_cell,
            setProps,
            virtual_dataframe_indices
        } = this.props;

        event.preventDefault();

        let newDataframe = dataframe;

        const columnIndexOffset =
            (row_deletable ? 1 : 0) +
            (row_selectable ? 1 : 0);

        const realCells: [number, number][] = R.map(
            cell => [virtual_dataframe_indices[cell[0]], cell[1] - columnIndexOffset] as [number, number],
            selected_cell
        );

        realCells.forEach(cell => {
            if (colIsEditable(editable, columns[cell[1]])) {
                newDataframe = R.set(
                    R.lensPath([cell[0], columns[cell[1]].id]),
                    '',
                    newDataframe
                );
            }
        });

        setProps({
            dataframe: newDataframe
        });
    }

    getNextCell = (event: any, { restrictToSelection, currentCell }: any) => {
        const { columns, row_deletable, row_selectable, selected_cell, virtualizer } = this.props;
        const dataframe = virtualizer.dataframe;

        const e = event;
        const vci: any[] = [];

        const columnIndexOffset =
            (row_deletable ? 1 : 0) +
            (row_selectable ? 1 : 0);

        if (!restrictToSelection) {
            columns.forEach((c, i) => {
                if (!c.hidden) {
                    vci.push(i + columnIndexOffset);
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
                        )
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
                        )
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
            row_deletable,
            row_selectable,
            selected_cell,
            virtualizer
        } = this.props;
        const dataframe = virtualizer.dataframe;

        const columnIndexOffset =
            (row_deletable ? 1 : 0) +
            (row_selectable ? 1 : 0);

        const noOffsetSelectedCells: [number, number][] = R.map(
            cell => [cell[0], cell[1] - columnIndexOffset] as [number, number],
            selected_cell
        );

        TableClipboardHelper.toClipboard(e, noOffsetSelectedCells, columns, dataframe);
        this.$el.focus();
    }

    onPaste = (e: any) => {
        const {
            active_cell,
            columns,
            dataframe,
            editable,
            filtering_settings,
            row_deletable,
            row_selectable,
            setProps,
            sorting_settings,
            virtual_dataframe_indices
        } = this.props;

        if (!editable) {
            return;
        }

        const columnIndexOffset =
            (row_deletable ? 1 : 0) +
            (row_selectable ? 1 : 0);

        const noOffsetActiveCell: [number, number] = [active_cell[0], active_cell[1] - columnIndexOffset];

        const result = TableClipboardHelper.fromClipboard(
            e,
            noOffsetActiveCell,
            virtual_dataframe_indices,
            columns,
            dataframe,
            true,
            !sorting_settings.length || !filtering_settings.length
        );

        if (result) {
            setProps(result);
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

    loadNext = () => {
        const { virtualizer } = this.props;

        virtualizer.loadNext();
    }

    loadPrevious = () => {
        const { virtualizer } = this.props;

        virtualizer.loadPrevious();
    }

    onContainerScroll = (ev: any) => {
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

    applyStyle = (columns: Columns, deletable: boolean, selectable: RowSelection) => {
        let typeIndex = 0;

        if (deletable) {

            this.stylesheet.setRule(
                `.dash-spreadsheet-inner td.column-${typeIndex}`,
                `width: 30px; max-width: 30px; min-width: 30px;`
            );
            this.stylesheet.setRule(
                `.dash-spreadsheet-inner th.column-${typeIndex}`,
                `width: 30px; max-width: 30px; min-width: 30px;`
            );

            ++typeIndex;
        }

        if (selectable) {
            this.stylesheet.setRule(
                `.dash-spreadsheet-inner td.column-${typeIndex}`,
                `width: 30px; max-width: 30px; min-width: 30px;`
            );
            this.stylesheet.setRule(
                `.dash-spreadsheet-inner th.column-${typeIndex}`,
                `width: 30px; max-width: 30px; min-width: 30px;`
            );

            ++typeIndex;
        }

        R.forEach(column => {
            const width = Stylesheet.unit(column.width || DEFAULT_CELL_WIDTH, 'px');
            const maxWidth = Stylesheet.unit(column.maxWidth || column.width || DEFAULT_CELL_WIDTH, 'px');
            const minWidth = Stylesheet.unit(column.minWidth || column.width || DEFAULT_CELL_WIDTH, 'px');

            this.stylesheet.setRule(
                `.dash-spreadsheet-inner td.column-${typeIndex}`,
                `width: ${width}; max-width: ${maxWidth}; min-width: ${minWidth};`
            );
            this.stylesheet.setRule(
                `.dash-spreadsheet-inner th.column-${typeIndex}`,
                `width: ${width}; max-width: ${maxWidth}; min-width: ${minWidth};`
            );

            ++typeIndex;
        }, columns);
    }

    renderFragment = (cells: any[][] | null) => (
        cells ?
            (<table tabIndex={-1}>
                <tbody>
                    {cells.map(
                        (row, idx) => <tr key={`row-${idx}`}>{row}</tr>)
                    }
                </tbody>
            </table>) :
            null
    )

    handleSetFilter = (filtering_settings: string) => this.props.setProps({ filtering_settings });

    getCells = () => {
        return [
            ...HeaderCellFactory.createHeaders(this.props),
            ...this.filterFactory.createFilters(),
            ...this.cellFactory.createCells()
        ];
    }

    getFragments = (cells: any, fixedColumns: number, fixedRows: number) => {
        // slice out fixed columns
        const fixedColumnCells = fixedColumns ?
            R.map(row =>
                row.splice(0, R.reduceWhile<JSX.Element, IAccumulator>(
                    acc => acc.count < fixedColumns,
                    (acc, cell) => {
                        acc.cells++;
                        acc.count += (cell.props.colSpan || 1);

                        return acc;
                    },
                    { cells: 0, count: 0 },
                    row as any
                ).cells),
                cells) :
            null;

        // slice out fixed rows
        const fixedRowCells = fixedRows ?
            cells.splice(0, fixedRows) :
            null;

        const fixedRowAndColumnCells = fixedRows && fixedColumnCells ?
            fixedColumnCells.splice(0, fixedRows) :
            null;

        return [
            [this.renderFragment(fixedRowAndColumnCells), this.renderFragment(fixedRowCells)],
            [this.renderFragment(fixedColumnCells), this.renderFragment(cells)]
        ];
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
            columns,
            n_fixed_columns,
            n_fixed_rows,
            row_deletable,
            row_selectable
        } = this.props;

        this.applyStyle(columns, row_deletable, row_selectable);

        const classes = [
            'dash-spreadsheet-inner',
            'dash-spreadsheet',
            ...(n_fixed_rows ? ['freeze-top'] : []),
            ...(n_fixed_columns ? ['freeze-left'] : [])
        ];

        const containerClasses = [
            'dash-spreadsheet',
            'dash-spreadsheet-container',
            ...(n_fixed_rows ? ['freeze-top'] : []),
            ...(n_fixed_columns ? ['freeze-left'] : [])
        ];

        const cells = this.getCells();
        const grid = this.getFragments(cells, n_fixed_columns, n_fixed_rows);

        return (<div
            id={id}
            onCopy={this.onCopy}
            onKeyDown={this.handleKeyDown}
            onPaste={this.onPaste}
        >
            <div className={containerClasses.join(' ')}>
                <div className={classes.join(' ')}>
                    {grid.map((row, rowIndex) => (<div
                        key={`r${rowIndex}`}
                        ref={`r${rowIndex}`}
                        className={`row row-${rowIndex}`}
                        onScroll={this.onScroll}
                    >{row.map((cell, columnIndex) => (<div
                        key={columnIndex}
                        ref={`r${rowIndex}c${columnIndex}`}
                        className={`cell cell-${rowIndex}-${columnIndex}`}
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
