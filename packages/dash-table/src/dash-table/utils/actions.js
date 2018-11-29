import * as R from 'ramda';

function getGroupedColumnIndices(column, columns, headerRowIndex) {
    const columnIndex = columns.indexOf(column);

    if (!column.name || (Array.isArray(column.name) && column.name.length < headerRowIndex)) {
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

export function deleteColumn(column, columns, headerRowIndex, props) {
    const { data} = props;
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
        active_cell: [],
        end_cell: [],
        selected_cells: [],
        start_cell: [0]
    };
}

export function editColumnName(column, columns, headerRowIndex, props) {
    const { groupIndexFirst, groupIndexLast } = getGroupedColumnIndices(
        column, columns, headerRowIndex, props
    );
    /* eslint no-alert: 0 */
    const newColumnName = window.prompt('Enter a new column name');
    let newColumns = R.clone(columns);
    R.range(groupIndexFirst, groupIndexLast + 1).map(i => {
        let namePath;
        if (R.type(columns[i].name) === 'Array') {
            namePath = [i, 'name', headerRowIndex];
        } else {
            namePath = [i, 'name'];
        }
        newColumns = R.set(R.lensPath(namePath), newColumnName, newColumns);
    });
    return {
        columns: newColumns
    };
}
