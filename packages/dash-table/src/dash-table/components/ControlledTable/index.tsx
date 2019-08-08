import React, { PureComponent } from 'react';

import * as R from 'ramda';
import Stylesheet from 'core/Stylesheet';
import {
    KEY_CODES,
    isCtrlMetaKey,
    isCtrlDown,
    isNavKey
} from 'dash-table/utils/unicode';
import * as actions from 'dash-table/utils/actions';
import ExportButton from 'dash-table/components/Export';
import { selectionBounds, selectionCycle } from 'dash-table/utils/navigation';
import { makeCell, makeSelection } from 'dash-table/derived/cell/cellProps';

import getScrollbarWidth from 'core/browser/scrollbarWidth';
import Logger from 'core/Logger';
import { arrayMap3 } from 'core/math/arrayZipMap';
import { memoizeOne } from 'core/memoizer';
import lexer from 'core/syntax-tree/lexer';

import TableClipboardHelper from 'dash-table/utils/TableClipboardHelper';
import { ControlledTableProps, ICellFactoryProps, TableAction, IColumn } from 'dash-table/components/Table/props';
import dropdownHelper from 'dash-table/components/dropdownHelper';

import getColumnFlag from 'dash-table/derived/header/columnFlag';
import derivedLabelsAndIndices from 'dash-table/derived/header/labelsAndIndices';
import derivedTable from 'dash-table/derived/table';
import derivedTableFragments from 'dash-table/derived/table/fragments';
import derivedTableFragmentStyles from 'dash-table/derived/table/fragmentStyles';
import derivedTooltips from 'dash-table/derived/table/tooltip';
import { derivedTableStyle } from 'dash-table/derived/style';
import { IStyle } from 'dash-table/derived/style/props';
import TableTooltip from './fragments/TableTooltip';

import queryLexicon from 'dash-table/syntax-tree/lexicon/query';

const DEFAULT_STYLE = {
    width: '100%'
};

export default class ControlledTable extends PureComponent<ControlledTableProps> {
    private readonly menuRef = React.createRef<HTMLDivElement>();
    private readonly stylesheet: Stylesheet = new Stylesheet(`#${this.props.id}`);
    private readonly tableFn = derivedTable(() => this.props);
    private readonly tableFragments = derivedTableFragments();
    private readonly tableStyle = derivedTableStyle();
    private readonly labelsAndIndices = derivedLabelsAndIndices();

    private calculateTableStyle = memoizeOne((style: Partial<IStyle>) => R.mergeAll(
        this.tableStyle(DEFAULT_STYLE, style)
    ));

    constructor(props: ControlledTableProps) {
        super(props);

        this.updateStylesheet();
    }

    getLexerResult = memoizeOne(lexer.bind(undefined, queryLexicon));

    get lexerResult() {
        const { filter_query } = this.props;

        return this.getLexerResult(filter_query);
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
            active_cell &&
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
        document.addEventListener('mousedown', this.handleClick);
        document.addEventListener('paste', this.handlePaste);
    }

    componentWillUnmount() {
        window.removeEventListener('resize', this.forceHandleResize);
        document.removeEventListener('mousedown', this.handleClick);
        document.removeEventListener('paste', this.handlePaste);
    }

    componentWillUpdate() {
        this.updateStylesheet();
    }

    componentDidUpdate() {
        this.applyStyle();
        this.handleResize();
        this.handleDropdown();
        this.adjustTooltipPosition();

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

    handleClick = (event: any) => {
        const $el = this.$el;

        if ($el &&
            !$el.contains(event.target as Node) &&
            /*
             * setProps is expensive, it causes excessive re-rendering in Dash.
             * so, only call when the table isn't already focussed, otherwise
             * the app will excessively re-render on _every click on the page_
             */
            this.props.is_focused
        ) {
            this.props.setProps({
                is_focused: false
            });
        }

        const menu = this.menuRef;

        if (this.props.activeMenu &&
            menu &&
            menu.current &&
            !menu.current.contains(event.target as Node)
        ) {
            this.props.setState({
                activeMenu: undefined
            });
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
            selected_cells,
            start_cell,
            end_cell,
            setProps,
            viewport,
            visibleColumns
        } = this.props;

        // This is mostly to prevent TABing also triggering native HTML tab
        // navigation. If the preventDefault is too greedy here we must
        // continue to use it for at least the case we are navigating with
        // TAB
        event.preventDefault();

        if (!active_cell) {
            // there should always be an active_cell if we got here...
            // but if for some reason there isn't, bail out rather than
            // doing something unexpected
            Logger.warning('Trying to change cell, but no cell is active.');
            return;
        }

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
                active_cell: nextCell,
                start_cell: nextCell,
                end_cell: nextCell
            });
            return;
        }

        // else we are navigating with arrow keys and extending selection
        // with shift.

        let {minRow, minCol, maxRow, maxCol} = selectionBounds(selected_cells);
        const selectingDown =
            e.keyCode === KEY_CODES.ARROW_DOWN || e.keyCode === KEY_CODES.ENTER;
        const selectingUp = e.keyCode === KEY_CODES.ARROW_UP;
        const selectingRight =
            e.keyCode === KEY_CODES.ARROW_RIGHT || e.keyCode === KEY_CODES.TAB;
        const selectingLeft = e.keyCode === KEY_CODES.ARROW_LEFT;
        let startRow = start_cell && start_cell.row;
        let startCol = start_cell && start_cell.column;
        let endRow = end_cell && end_cell.row;
        let endCol = end_cell && end_cell.column;

        if (selectingDown) {
            if (active_cell.row > minRow) {
                minRow++;
                endRow = minRow;
            } else if (maxRow < viewport.data.length - 1) {
                maxRow++;
                endRow = maxRow;
            }
        } else if (selectingUp) {
            if (active_cell.row < maxRow) {
                maxRow--;
                endRow = maxRow;
            } else if (minRow > 0) {
                minRow--;
                endRow = minRow;
            }
        } else if (selectingRight) {
            if (active_cell.column > minCol) {
                minCol++;
                endCol = minCol;
            } else if (maxCol < visibleColumns.length - 1) {
                maxCol++;
                endCol = maxCol;
            }
        } else if (selectingLeft) {
            if (active_cell.column < maxCol) {
                maxCol--;
                endCol = maxCol;
            } else if (minCol > 0) {
                minCol--;
                endCol = minCol;
            }
        } else {
            return;
        }

        const finalSelected = makeSelection(
            {minRow, maxRow, minCol, maxCol},
            visibleColumns, viewport
        );

        const newProps: Partial<ICellFactoryProps> = {
            is_focused: false,
            end_cell: makeCell(endRow, endCol, visibleColumns, viewport),
            selected_cells: finalSelected
        };

        const newStartRow = endRow === minRow ? maxRow : minRow;
        const newStartCol = endCol === minCol ? maxCol : minCol;

        if (startRow !== newStartRow || startCol !== newStartCol) {
            newProps.start_cell = makeCell(
                newStartRow,
                newStartCol,
                visibleColumns,
                viewport
            );
        }

        setProps(newProps);
    }

    deleteCell = (event: any) => {
        const {
            data,
            selected_cells,
            setProps,
            viewport,
            visibleColumns
        } = this.props;

        event.preventDefault();

        let newData = data;

        const realCells: [number, number][] = R.map(
            cell => [viewport.indices[cell.row], cell.column] as [number, number],
            selected_cells
        );

        realCells.forEach(cell => {
            if (visibleColumns[cell[1]].editable) {
                newData = R.set(
                    R.lensPath([cell[0], visibleColumns[cell[1]].id]),
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
        const { selected_cells, viewport, visibleColumns } = this.props;

        const e = event;

        const {row, column} = currentCell;
        let nextCoords;

        switch (e.keyCode) {
            case KEY_CODES.ARROW_LEFT:
                nextCoords = restrictToSelection
                    ? selectionCycle([row, column - 1], selected_cells)
                    : [row, R.max(0, column - 1)];
                break;

            case KEY_CODES.ARROW_RIGHT:
            case KEY_CODES.TAB:
                nextCoords = restrictToSelection
                    ? selectionCycle([row, column + 1], selected_cells)
                    : [row, R.min(visibleColumns.length - 1, column + 1)];
                break;

            case KEY_CODES.ARROW_UP:
                nextCoords = restrictToSelection
                    ? selectionCycle([row - 1, column], selected_cells)
                    : [R.max(0, row - 1), column];
                break;

            case KEY_CODES.ARROW_DOWN:
            case KEY_CODES.ENTER:
                nextCoords = restrictToSelection
                    ? selectionCycle([row + 1, column], selected_cells)
                    : [R.min(viewport.data.length - 1, row + 1), column];
                break;

            default:
                throw new Error(
                    `Table.getNextCell: unknown navigation keycode ${e.keyCode}`
                );
        }
        return makeCell(nextCoords[0], nextCoords[1], visibleColumns, viewport);
    }

    onCopy = (e: any) => {
        const {
            selected_cells,
            viewport,
            columns,
            visibleColumns,
            include_headers_on_copy_paste
        } = this.props;

        TableClipboardHelper.toClipboard(e, selected_cells, columns, visibleColumns, viewport.data, include_headers_on_copy_paste);
        this.$el.focus();
    }

    onPaste = (e: any) => {
        const {
            active_cell,
            data,
            editable,
            filter_query,
            setProps,
            sort_by,
            viewport,
            visibleColumns,
            include_headers_on_copy_paste
        } = this.props;

        if (!editable || !active_cell) {
            return;
        }

        const result = TableClipboardHelper.fromClipboard(
            e,
            active_cell,
            viewport.indices,
            visibleColumns,
            data,
            true,
            !sort_by.length || !filter_query.length,
            include_headers_on_copy_paste
        );

        if (result) {
            setProps(result);
        }
    }

    get displayPagination() {
        const {
            data,
            page_action,
            page_size
        } = this.props;

        return (
            page_action === TableAction.Native &&
            page_size < data.length
        ) || page_action === TableAction.Custom;
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
            fixed_columns,
            fixed_rows,
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
        if (fixed_rows) {
            Array.from(r1c1.querySelectorAll('tr:first-of-type td, tr:first-of-type th')).forEach((td, index) => {
                const style = getComputedStyle(td);
                const width = style.width;

                this.stylesheet.setRule(
                    `.dash-fixed-row:not(.dash-fixed-column) th:nth-of-type(${index + 1})`,
                    `width: ${width} !important; min-width: ${width} !important; max-width: ${width} !important;`
                );
            });
        }

        // Adjust the width of the fixed row / fixed columns header
        if (fixed_columns && fixed_rows) {
            Array.from(r1c0.querySelectorAll('tr:first-of-type td, tr:first-of-type th')).forEach((td, index) => {
                const style = getComputedStyle(td);
                const width = style.width;

                this.stylesheet.setRule(
                    `.dash-fixed-column.dash-fixed-row th:nth-of-type(${index + 1})`,
                    `width: ${width} !important; min-width: ${width} !important; max-width: ${width} !important;`
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
        this.adjustTooltipPosition();
    }

    render() {
        const {
            columns,
            id,
            tooltip_conditional,
            tooltip,
            currentTooltip,
            fill_width,
            filter_action,
            fixed_columns,
            fixed_rows,
            scrollbarWidth,
            style_as_list_view,
            style_table,
            tooltip_delay,
            tooltip_duration,
            tooltip_data,
            uiCell,
            uiHeaders,
            uiViewport,
            viewport,
            virtualized,
            virtualization,
            visibleColumns
        } = this.props;

        const fragmentClasses = [
            [
                fixed_rows && fixed_columns ? 'dash-fixed-row dash-fixed-column' : '',
                fixed_rows ? 'dash-fixed-row' : ''
            ],
            [
                fixed_columns ? 'dash-fixed-column' : '',
                'dash-fixed-content'
            ]
        ];

        const rawTable = this.tableFn();
        const { grid, empty } = this.tableFragments(
            fixed_columns,
            fixed_rows,
            rawTable,
            virtualized.offset.rows
        );

        const classes = [
            'dash-spreadsheet',
            ...(virtualization ? ['dash-virtualized'] : []),
            ...(fixed_rows ? ['dash-freeze-top'] : []),
            ...(fixed_columns ? ['dash-freeze-left'] : []),
            ...(style_as_list_view ? ['dash-list-view'] : []),
            ...(empty[0][1] ? ['dash-empty-01'] : []),
            ...(empty[1][1] ? ['dash-empty-11'] : []),
            ...(visibleColumns.length ? [] : ['dash-no-columns']),
            ...(virtualized.data.length ? [] : ['dash-no-data']),
            ...(filter_action !== TableAction.None ? [] : ['dash-no-filter']),
            ...(fill_width ? ['dash-fill-width'] : [])
        ];

        const containerClasses = ['dash-spreadsheet-container', ...classes];
        const innerClasses = ['dash-spreadsheet-inner', ...classes];

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

    /* Tooltip */
        let tableTooltip = derivedTooltips(
            currentTooltip,
            tooltip_data,
            tooltip_conditional,
            tooltip,
            virtualized,
            tooltip_delay,
            tooltip_duration
        );

        const { export_format, export_headers, virtual, merge_duplicate_headers } = this.props;
        const buttonProps = {
            export_format,
            virtual_data: virtual,
            columns,
            visibleColumns,
            export_headers,
            merge_duplicate_headers
        };

        return (<div
            id={id}
            onCopy={this.onCopy}
            onKeyDown={this.handleKeyDown}
            onPaste={this.onPaste}
            style={{ position: 'relative' }}
        >
            <TableTooltip
                key='tooltip'
                ref='tooltip'
                className='dash-table-tooltip'
                tooltip={tableTooltip}
            />
            <div className='dash-spreadsheet-menu'>
                {this.renderMenu()}
                <ExportButton {...buttonProps} />
            </div>
            <div className={containerClasses.join(' ')} style={tableStyle}>
                <div
                    ref='table'
                    className={innerClasses.join(' ')}
                    style={tableStyle}
                >
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

    renderMenu() {
        if (!this.showToggleColumns) {
            return null;
        }

        const {
            activeMenu,
            columns,
            hidden_columns,
            merge_duplicate_headers,
            setState
        } = this.props;

        const labelsAndIndices = this.labelsAndIndices(columns, columns, merge_duplicate_headers);
        const lastRow = labelsAndIndices.length - 1;

        return (<div
            className='dash-spreadsheet-menu-item'
            ref={this.menuRef}
        >
            <button className='show-hide'
                onClick={() => setState({
                    activeMenu: activeMenu === 'show/hide' ? undefined : 'show/hide'
                })}
            >Toggle Columns</button>
            {activeMenu !== 'show/hide' ?
                null :
                <div className='show-hide-menu'>
                    {R.unnest(labelsAndIndices.map(([, indices], i) => indices.map((index, j) => {
                        const spansAllColumns = indices.length === 1;
                        const column = columns[index];

                        const checked = !hidden_columns || hidden_columns.indexOf(column.id) < 0;
                        const hideable = getColumnFlag(i, lastRow, column.hideable);

                        const disabled = (spansAllColumns && checked) || (!hideable && checked);

                        return {
                            i: index,
                            j,
                            component: !hideable ? null : (<div className='show-hide-menu-item'>
                                <input
                                    type='checkbox'
                                    checked={checked}
                                    disabled={disabled}
                                    onClick={this.toggleColumn.bind(this, column, i, merge_duplicate_headers)}
                                />
                                <label>{!column.name ?
                                    column.id :
                                    typeof column.name === 'string' ?
                                        column.name :
                                        column.name.slice(0, i + 1).filter(name => name.length !== 0).join(' | ')
                                }</label>
                            </div>)
                        };
                    }))).filter(i => !R.isNil(i)).sort((a, b) => (a.i - b.i) || (a.j - b.j)).map(a => a.component)}
                </div>
            }
        </div>);
    }

    private adjustTooltipPosition() {
        const { currentTooltip, virtualized } = this.props;

        if (!currentTooltip) {
            return;
        }

        const id = currentTooltip.id;
        const row = currentTooltip.row - virtualized.offset.rows;

        const { table, tooltip: t } = this.refs as { [key: string]: any };

        if (t) {
            const cell = table.querySelector(`td[data-dash-column="${id}"][data-dash-row="${row}"]`);

            (this.refs.tooltip as TableTooltip).updateBounds(cell);
        }
    }

    private get showToggleColumns(): boolean {
        const {
            columns,
            hidden_columns
        } = this.props;

        return (
            hidden_columns && hidden_columns.length > 0) ||
            R.any(column => !!column.hideable, columns);
    }

    private toggleColumn = (column: IColumn, headerRowIndex: number, mergeDuplicateHeaders: boolean) => {
        const {
            columns,
            hidden_columns: base,
            setProps
        } = this.props;

        const ids: string[] = actions.getColumnIds(column, columns, headerRowIndex, mergeDuplicateHeaders);

        const hidden_columns = base ? base.slice(0) : [];
        R.forEach(id => {
            const cIndex = hidden_columns.indexOf(id);

            if (cIndex >= 0) {
                hidden_columns.splice(cIndex, 1);
            } else {
                hidden_columns.push(id);
            }
        }, ids);

        setProps({ hidden_columns });
    }
}
