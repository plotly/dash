import * as R from 'ramda';
import { SelectedCells, ICellFactoryProps } from 'dash-table/components/Table/props';
import isActive from 'dash-table/derived/cell/isActive';

function isCellSelected(selectedCells: SelectedCells, idx: number, i: number) {
    return selectedCells && R.contains([idx, i], selectedCells);
}

export const handleClick = (propsFn: () => ICellFactoryProps, idx: number, i: number, e: any) => {
    const {
        editable,
        selected_cells,
        setProps,
        virtualized
    } = propsFn();

    if (!editable) {
        return;
    }

    const selected = isCellSelected(selected_cells, idx, i);

    // don't update if already selected
    if (selected) {
        return;
    }

    e.preventDefault();
    const cellLocation: [number, number] = [
        idx + virtualized.offset.rows,
        i + virtualized.offset.columns
    ];

    const newProps: Partial<ICellFactoryProps> = {
        is_focused: false,
        active_cell: cellLocation
    };

    const selectedRows = R.uniq(R.pluck(0, selected_cells)).sort((a, b) => a - b);
    const selectedCols = R.uniq(R.pluck(1, selected_cells)).sort((a, b) => a - b);
    const minRow = selectedRows[0];
    const minCol = selectedCols[0];

    if (e.shiftKey) {
        newProps.selected_cells = R.xprod(
            R.range(
                R.min(minRow, cellLocation[0]),
                R.max(minRow, cellLocation[0]) + 1
            ),
            R.range(
                R.min(minCol, cellLocation[1]),
                R.max(minCol, cellLocation[1]) + 1
            )
        ) as any;
    } else {
        newProps.selected_cells = [cellLocation];
    }

    setProps(newProps);
};

export const handleDoubleClick = (propsFn: () => ICellFactoryProps, idx: number, i: number, e: any) => {
    const {
        editable,
        is_focused,
        setProps,
        virtualized
    } = propsFn();

    if (!editable) {
        return;
    }

    const cellLocation: [number, number] = [
        idx + virtualized.offset.rows,
        i + virtualized.offset.columns
    ];

    if (!is_focused) {
        e.preventDefault();
        const newProps = {
            selected_cells: [cellLocation],
            active_cell: cellLocation,
            is_focused: true
        };
        setProps(newProps);
    }
};

export const handleChange = (propsFn: () => ICellFactoryProps, idx: number, i: number, value: any) => {
    const {
        columns,
        data,
        editable,
        setProps,
        virtualized
    } = propsFn();

    const c = columns[i];
    const realIdx = virtualized.indices[idx];

    if (!editable) {
        return;
    }

    const newData = R.set(
        R.lensPath([realIdx, c.id]),
        value,
        data
    );
    setProps({
        data: newData
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

export const handlePaste = (_propsFn: () => ICellFactoryProps, _idx: number, _i: number, e: ClipboardEvent) => {
    e.preventDefault();
};