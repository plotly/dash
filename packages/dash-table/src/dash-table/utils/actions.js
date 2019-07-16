import * as R from 'ramda';
import getHeaderRows from 'dash-table/derived/header/headerRows';

function getGroupedColumnIndices(column, columns, headerRowIndex, mergeDuplicateHeaders, columnIndex) {
    if (!column.name || (Array.isArray(column.name) && column.name.length < headerRowIndex) || !mergeDuplicateHeaders) {
        return { groupIndexFirst: columnIndex, groupIndexLast: columnIndex };
    }
    let lastColumnIndex = columnIndex;

    for (let i = columnIndex; i < columns.length; ++i) {
        const c = columns[i];

        if (c.name && Array.isArray(c.name) && c.name.length > headerRowIndex && c.name[headerRowIndex] === column.name[headerRowIndex]) {
            lastColumnIndex = i;
        } else {
            break;
        }
    }
    return { groupIndexFirst: columnIndex, groupIndexLast: lastColumnIndex };
}

export function deleteColumn(column, columns, headerRowIndex, data) {
    const {groupIndexFirst, groupIndexLast} = getGroupedColumnIndices(
        column, columns, headerRowIndex
    );
    const rejectedColumnIds = R.slice(
        groupIndexFirst,
        groupIndexLast + 1,
        R.pluck('id', columns)
    );
    return {
        columns: R.remove(
            groupIndexFirst,
            1 + groupIndexLast - groupIndexFirst,
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

export const clearSelection = {
    active_cell: undefined,
    start_cell: undefined,
    end_cell: undefined,
    selected_cells: []
};

export function changeColumnHeader(column, columns, headerRowIndex, mergeDuplicateHeaders, newColumnName) {
    let newColumns = columns;
    const maxLength = getHeaderRows(newColumns);
    const columnIndex = newColumns.findIndex(col => col.id === column.id);

    if (typeof column.name === 'string' && maxLength > 1) {
        const newColumnNames = Array(maxLength).fill(column.name);
        const cloneColumn = R.mergeRight(column, {name: newColumnNames});
        newColumns = newColumns.slice(0);
        newColumns[columnIndex] = cloneColumn;
    }

    const { groupIndexFirst, groupIndexLast } = getGroupedColumnIndices(
        column, newColumns, headerRowIndex, mergeDuplicateHeaders, columnIndex
    );

    R.range(groupIndexFirst, groupIndexLast + 1).map(i => {
        let namePath;
        if (R.type(newColumns[i].name) === 'Array') {
            namePath = [i, 'name', headerRowIndex];
        }
        newColumns = R.set(R.lensPath(namePath), newColumnName, newColumns);
    });

    return { columns: newColumns} ;
}

export function editColumnName(column, columns, headerRowIndex, mergeDuplicateHeaders) {
    const newColumnName = window.prompt('Enter a new column name');
    return changeColumnHeader(column, columns, headerRowIndex, mergeDuplicateHeaders, newColumnName);
}
