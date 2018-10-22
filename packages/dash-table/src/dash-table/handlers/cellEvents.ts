import * as R from 'ramda';
import { SelectedCells, ICellFactoryOptions } from 'dash-table/components/Table/props';

function isCellSelected(selectedCells: SelectedCells, idx: number, i: number) {
    return selectedCells && R.contains([idx, i], selectedCells);
}

export const handleClick = (propsFn: () => ICellFactoryOptions, idx: number, i: number, e: any) => {
    const {
        editable,
        is_focused,
        selected_cell,
        setProps
    } = propsFn();

    const selected = isCellSelected(selected_cell, idx, i);

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
    const cellLocation: [number, number] = [idx, i];
    const newProps: Partial<ICellFactoryOptions> = {
        is_focused: false,
        active_cell: cellLocation
    };

    const selectedRows = R.uniq(R.pluck(0, selected_cell)).sort((a, b) => a - b);
    const selectedCols = R.uniq(R.pluck(1, selected_cell)).sort((a, b) => a - b);
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
        ) as any;
    } else {
        newProps.selected_cell = [cellLocation];
    }

    setProps(newProps);
};

export const handleDoubleClick = (propsFn: () => ICellFactoryOptions, idx: number, i: number, e: any) => {
    const {
        editable,
        is_focused,
        setProps
    } = propsFn();

    if (!editable) {
        return;
    }

    const cellLocation: [number, number] = [idx, i];

    if (!is_focused) {
        e.preventDefault();
        const newProps = {
            selected_cell: [cellLocation],
            active_cell: cellLocation,
            is_focused: true
        };
        setProps(newProps);
    }
};

export const handleChange = (propsFn: () => ICellFactoryOptions, idx: number, i: number, value: any) => {
    const {
        columns,
        data,
        editable,
        setProps,
        viewport
    } = propsFn();

    const c = columns[i];
    const realIdx = viewport.indices[idx];

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

export const handlePaste = (_propsFn: () => ICellFactoryOptions, _idx: number, _i: number, e: ClipboardEvent) => {
    e.preventDefault();
};