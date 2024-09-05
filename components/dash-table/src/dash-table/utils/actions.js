import * as R from 'ramda';
import getHeaderRows from 'dash-table/derived/header/headerRows';

function getGroupedColumnIndices(
    column,
    columns,
    headerRowIndex,
    mergeDuplicateHeaders,
    columnIndex,
    backwardLooking = false
) {
    if (
        !column.name ||
        (Array.isArray(column.name) && column.name.length < headerRowIndex) ||
        !mergeDuplicateHeaders
    ) {
        return {groupIndexFirst: columnIndex, groupIndexLast: columnIndex};
    }

    // backward looking
    if (backwardLooking) {
        for (let i = columnIndex; i >= 0; --i) {
            const c = columns[i];

            if (
                c.name &&
                Array.isArray(c.name) &&
                c.name.length > headerRowIndex &&
                c.name[headerRowIndex] === column.name[headerRowIndex]
            ) {
                columnIndex = i;
            } else {
                break;
            }
        }
    }

    let lastColumnIndex = columnIndex;

    // forward looking
    for (let i = columnIndex; i < columns.length; ++i) {
        const c = columns[i];

        if (
            c.name &&
            Array.isArray(c.name) &&
            c.name.length > headerRowIndex &&
            c.name[headerRowIndex] === column.name[headerRowIndex]
        ) {
            lastColumnIndex = i;
        } else {
            break;
        }
    }

    return {groupIndexFirst: columnIndex, groupIndexLast: lastColumnIndex};
}

export function getAffectedColumns(
    column,
    columns,
    headerRowIndex,
    mergeDuplicateHeaders,
    backwardLooking = false
) {
    const {groupIndexFirst, groupIndexLast} = getGroupedColumnIndices(
        column,
        columns,
        headerRowIndex,
        mergeDuplicateHeaders,
        columns.indexOf(column),
        backwardLooking
    );

    return R.slice(groupIndexFirst, groupIndexLast + 1, R.pluck('id', columns));
}

export function clearColumn(
    column,
    columns,
    visibleColumns,
    headerRowIndex,
    mergeDuplicateHeaders,
    _data
) {
    const {data} = deleteColumn(
        column,
        columns,
        visibleColumns,
        headerRowIndex,
        mergeDuplicateHeaders,
        _data
    );
    return {data};
}

export function deleteColumn(
    column,
    columns,
    visibleColumns,
    headerRowIndex,
    mergeDuplicateHeaders,
    data
) {
    const rejectedColumnIds = getAffectedColumns(
        column,
        visibleColumns,
        headerRowIndex,
        mergeDuplicateHeaders
    );

    return {
        columns: R.filter(
            col => rejectedColumnIds.indexOf(col.id) === -1,
            columns
        ),
        data: R.map(R.omit(rejectedColumnIds), data),
        // NOTE - We're just clearing these so that there aren't any
        // inconsistencies. In an ideal world, we would probably only
        // update them if they contained one of the columns that we're
        // trying to delete
        ...clearSelection
    };
}

export function getColumnIds(
    column,
    columns,
    headerRowIndex,
    mergeDuplicateHeaders
) {
    const {groupIndexFirst, groupIndexLast} = getGroupedColumnIndices(
        column,
        columns,
        headerRowIndex,
        mergeDuplicateHeaders,
        columns.indexOf(column)
    );

    return R.map(c => c.id, columns.slice(groupIndexFirst, groupIndexLast + 1));
}

export const clearSelection = {
    active_cell: undefined,
    start_cell: undefined,
    end_cell: undefined,
    selected_cells: []
};

export function changeColumnHeader(
    column,
    columns,
    headerRowIndex,
    mergeDuplicateHeaders,
    newColumnName
) {
    let newColumns = columns;
    const maxLength = getHeaderRows(newColumns);
    const columnIndex = newColumns.findIndex(col => col.id === column.id);

    if (typeof column.name === 'string' && maxLength > 1) {
        const newColumnNames = Array(maxLength).fill(column.name);
        const cloneColumn = R.mergeRight(column, {name: newColumnNames});
        newColumns = newColumns.slice(0);
        newColumns[columnIndex] = cloneColumn;
    }

    const {groupIndexFirst, groupIndexLast} = getGroupedColumnIndices(
        column,
        newColumns,
        headerRowIndex,
        mergeDuplicateHeaders,
        columnIndex,
        true
    );

    R.range(groupIndexFirst, groupIndexLast + 1).map(i => {
        const namePath = [i, 'name'];
        if (R.type(newColumns[i].name) === 'Array') {
            namePath.push(headerRowIndex);
        }
        newColumns = R.set(R.lensPath(namePath), newColumnName, newColumns);
    });

    return {columns: newColumns};
}

export function editColumnName(
    column,
    columns,
    headerRowIndex,
    mergeDuplicateHeaders
) {
    const newColumnName = window.prompt('Enter a new column name');
    if (newColumnName === null) {
        return null;
    }
    return changeColumnHeader(
        column,
        columns,
        headerRowIndex,
        mergeDuplicateHeaders,
        newColumnName
    );
}
