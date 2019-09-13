import { min, max, set, lensPath } from 'ramda';
import { ICellFactoryProps } from 'dash-table/components/Table/props';
import isActive from 'dash-table/derived/cell/isActive';
import isSelected from 'dash-table/derived/cell/isSelected';
import { makeCell, makeSelection } from 'dash-table/derived/cell/cellProps';
import reconcile from 'dash-table/type/reconcile';

export const handleClick = (
    propsFn: () => ICellFactoryProps,
    idx: number,
    i: number,
    e: any
) => {
    const {
        selected_cells,
        active_cell,
        setProps,
        viewport,
        virtualized,
        visibleColumns
    } = propsFn();

    const col = i + virtualized.offset.columns;

    const clickedCell = makeCell(idx, col, visibleColumns, viewport);

    // clicking again on the already-active cell: ignore
    if (active_cell && idx === active_cell.row && col === active_cell.column) {
        return;
    }

    e.preventDefault();

    /*
     * In some cases this will initiate browser text selection.
     * We've hijacked copying, so while it might be nice to allow copying part
     * of a cell, currently you'll always get the whole cell regardless of what
     * the browser thinks is selected.
     * And when you've selected multiple cells the browser selection is
     * completely wrong.
     */
    const browserSelection = window.getSelection();
    if (browserSelection) {
        browserSelection.removeAllRanges();
    }

    const selected = isSelected(selected_cells, idx, col);

    // if clicking on a *different* already-selected cell (NOT shift-clicking,
    // not the active cell), don't alter the selection,
    // just move the active cell
    if (selected && !e.shiftKey) {
        setProps({
            is_focused: false,
            active_cell: clickedCell
        });
        return;
    }

    const newProps: Partial<ICellFactoryProps> = {
        is_focused: false,
        end_cell: clickedCell
    };

    if (e.shiftKey && active_cell) {
        newProps.selected_cells = makeSelection(
            {
                minRow: min(idx, active_cell.row),
                maxRow: max(idx, active_cell.row),
                minCol: min(col, active_cell.column),
                maxCol: max(col, active_cell.column)
            },
            visibleColumns,
            viewport
        );
    } else {
        newProps.active_cell = clickedCell;
        newProps.start_cell = clickedCell;
        newProps.selected_cells = [clickedCell];
    }

    setProps(newProps);
};

export const handleDoubleClick = (propsFn: () => ICellFactoryProps, idx: number, i: number, e: any) => {
    const {
        is_focused,
        setProps,
        viewport,
        virtualized,
        visibleColumns
    } = propsFn();

    const c = visibleColumns[i];

    if (!c.editable) {
        return;
    }

    const newCell = makeCell(
        idx,
        i + virtualized.offset.columns,
        visibleColumns, viewport
    );

    if (!is_focused) {
        e.preventDefault();
        const newProps = {
            selected_cells: [newCell],
            active_cell: newCell,
            start_cell: newCell,
            end_cell: newCell,
            is_focused: true
        };
        setProps(newProps);
    }
};

export const handleChange = (propsFn: () => ICellFactoryProps, idx: number, i: number, value: any) => {
    const {
        data,
        setProps,
        virtualized,
        visibleColumns
    } = propsFn();

    const c = visibleColumns[i];
    const realIdx = virtualized.indices[idx - virtualized.offset.rows];

    if (!c.editable) {
        return;
    }

    const result = reconcile(value, c);

    if (!result.success) {
        return;
    }

    const newData = set(
        lensPath([realIdx, c.id]),
        result.value,
        data
    );
    setProps({
        data: newData
    });

};

export const handleEnter = (propsFn: () => ICellFactoryProps, idx: number, i: number) => {
    const {
        setState,
        virtualized,
        visibleColumns
    } = propsFn();

    const c = visibleColumns[i];
    const realIdx = virtualized.indices[idx - virtualized.offset.rows];

    setState({
        currentTooltip: {
            id: c.id,
            row: realIdx
        }
    });
};

export const handleLeave = (propsFn: () => ICellFactoryProps, _idx: number, _i: number) => {
    const {
        setState
    } = propsFn();

    setState({ currentTooltip: undefined });
};

export const handleMove = (propsFn: () => ICellFactoryProps, idx: number, i: number) => {
    const {
        currentTooltip,
        setState,
        virtualized,
        visibleColumns
    } = propsFn();

    const c = visibleColumns[i];
    const realIdx = virtualized.indices[idx - virtualized.offset.rows];

    if (currentTooltip && currentTooltip.id === c.id && currentTooltip.row === realIdx) {
        return;
    }

    setState({
        currentTooltip: {
            id: c.id,
            row: realIdx
        }
    });
};

export const handleOnMouseUp = (propsFn: () => ICellFactoryProps, idx: number, i: number, e: any) => {
    const {
        active_cell,
        is_focused
    } = propsFn();

    const active = isActive(active_cell, idx, i);

    if (!is_focused && active) {
        e.preventDefault();
        // We do this because mouseMove can change the selection, we don't want
        // to check for all mouse movements, for performance reasons.
        const input = e.target;
        input.setSelectionRange(0, input.value ? input.value.length : 0);
    }
};

export const handlePaste = (_propsFn: () => ICellFactoryProps, _idx: number, _i: number, e: any) => {
    e.preventDefault();
};
