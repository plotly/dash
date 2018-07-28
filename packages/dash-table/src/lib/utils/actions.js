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
        newProps.start_cell = [0];
    }
    if (R.is(Array, selected_rows) && R.contains(rowIndex, selected_rows)) {
        newProps.selected_rows = R.without([rowIndex], selected_rows);
    }
    return newProps;
}
