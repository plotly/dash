import * as R from 'ramda';

import {SelectedCells} from 'dash-table/components/Table/props';

export default (selectedCells: SelectedCells, row: number, column: number) =>
    R.any(cell => cell.row === row && cell.column === column, selectedCells);
