import * as R from 'ramda';


export function deleteRow(rowIndex, props) {
    const {
        active_cell,
        dataframe,
        end_cell,
        selected_cell,
        selected_rows,
        start_cell
    } = props;
    const newProps = {
        dataframe: R.remove(rowIndex, 1, dataframe),
    };
    if (R.is(Array, active_cell) && active_cell[0] === rowIndex) {
        newProps.active_cell = [];
    }
    if (R.is(Array, end_cell) && end_cell[0] === rowIndex) {
        newProps.end_cell = [];
    }
    if (R.is(Array, selected_cell) && selected_cell[0] === rowIndex) {
        newProps.selected_cell = [];
    }
    if (R.is(Array, start_cell) && start_cell[0] === rowIndex) {
        newProps.start_cell = [0, 0];
    }
    if (R.is(Array, selected_rows) && R.contains(rowIndex, selected_rows)) {
        newProps.selected_rows = R.without([rowIndex], selected_rows);
    }
    return newProps;
}


function getGroupedColumnIndices(column, headerRowIndex, props) {
    // Find the set of column indices that share the same name and are adjacent
    // as the given column ("group")
    const {columns} = props;

    // if the columns are merged, then deleting will delete all of the
    // merged columns
    let columnName;
    let names;
    if (R.type(headerRowIndex) !== 'Null') {
        columnName = column.name[headerRowIndex];
        names = R.pluck(
            headerRowIndex,
            R.pluck('name', columns)
        );
    } else {
        columnName = column.name;
        names = R.pluck('name', columns);
    }
    const columnIndex = R.findIndex(R.propEq('id', column.id), columns);
    let groupIndexFirst = columnIndex;
    let groupIndexLast = columnIndex;
    while(names[groupIndexFirst - 1] === columnName) {
        groupIndexFirst--;
    }

    while(names[groupIndexLast + 1] === columnName) {
        groupIndexLast++;
    }

    return {groupIndexFirst, groupIndexLast};
}

export function deleteColumn(column, headerRowIndex, props) {
    const {columns, dataframe} = props;
    const {groupIndexFirst, groupIndexLast} = getGroupedColumnIndices(
        column, headerRowIndex, props
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
        dataframe: R.map(R.omit(rejectedColumnIds), dataframe),
        // NOTE - We're just clearing these so that there aren't any
        // inconsistencies. In an ideal world, we would probably only
        // update them if they contained one of the columns that we're
        // trying to delete
        active_cell: [],
        end_cell: [],
        selected_cell: [],
        start_cell: [0]
    }
}

export function editColumnName(column, headerRowIndex, props) {
    const {columns} = props;
    const {groupIndexFirst, groupIndexLast} = getGroupedColumnIndices(
        column, headerRowIndex, props
    );
    /* eslint no-alert: 0 */
    const newColumnName = window.prompt('Enter a new column name');
    let newColumns = R.clone(columns);
    R.range(groupIndexFirst, groupIndexLast+1).map(i => {
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
    }
}
