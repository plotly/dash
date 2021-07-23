import * as R from 'ramda';

import Logger from 'core/Logger';

import {
    ICellCoordinates,
    Columns,
    Data,
    ColumnType
} from 'dash-table/components/Table/props';
import reconcile from 'dash-table/type/reconcile';

export default (
    values: any[][],
    activeCell: ICellCoordinates,
    derived_viewport_indices: number[],
    columns_: Columns,
    visibleColumns: Columns,
    data: Data,
    overflowColumns = true,
    overflowRows = true
): {data: Data; columns: Columns} | void => {
    if (!overflowRows) {
        Logger.debug(
            'Clipboard -- Sorting or filtering active, do not create new rows'
        );
    }

    if (!overflowColumns) {
        Logger.debug('Clipboard -- Do not create new columns');
    }

    // don't modify the data and columns directly -- we may abort the paste
    // Individual rows will be modified, needs to be a deep clone
    let newData = R.clone(data);
    // Might add columns, not modifying the columns themselves, shallow clone is sufficient
    let newColumns = columns_.slice(0);
    let newVisibleColumns = visibleColumns.slice(0);

    if (
        overflowColumns &&
        values[0].length + (activeCell as any).column >= visibleColumns.length
    ) {
        const _newColumns = [];
        for (
            let i = visibleColumns.length;
            i < values[0].length + (activeCell as any).column;
            i++
        ) {
            _newColumns.push({
                id: `Column ${i + 1}`,
                name: `Column ${i + 1}`,
                type: ColumnType.Any,
                sort_as_null: []
            } as any);
            newData.forEach(row => (row[`Column ${i}`] = ''));
        }

        newColumns = R.insertAll(
            R.indexOf(R.last(visibleColumns), columns_) + 1,
            _newColumns,
            newColumns
        );

        newVisibleColumns = R.concat(newVisibleColumns, _newColumns);
    }

    const realActiveRow = derived_viewport_indices[(activeCell as any).row];
    if (overflowRows && values.length + realActiveRow >= data.length) {
        const emptyRow: any = {};
        visibleColumns.forEach(c => (emptyRow[c.id] = ''));
        newData = R.concat(
            newData,
            R.repeat(emptyRow, values.length + realActiveRow - data.length)
        );
    }

    const lastEntry = derived_viewport_indices.slice(-1)[0] || 0;
    const viewportSize = derived_viewport_indices.length;

    for (const [i, row] of values.entries()) {
        for (const [j, value] of row.entries()) {
            const viewportIndex = (activeCell as any).row + i;

            const iRealCell: number | undefined =
                viewportSize > viewportIndex
                    ? derived_viewport_indices[viewportIndex]
                    : overflowRows
                    ? lastEntry + (viewportIndex - viewportSize + 1)
                    : undefined;

            if (iRealCell === undefined) {
                continue;
            }

            const jOffset = (activeCell as any).column + j;
            const col = newVisibleColumns[jOffset];
            if (!col || !col.editable) {
                continue;
            }

            const coerced = reconcile(value, col);

            if (!coerced.success) {
                continue;
            }

            newData = R.set(
                R.lensPath([iRealCell, col.id]),
                coerced.value,
                newData
            );
        }
    }

    return {data: newData, columns: newColumns};
};
