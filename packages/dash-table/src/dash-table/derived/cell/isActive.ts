import { ActiveCell } from 'dash-table/components/Table/props';

export default (
    activeCell: ActiveCell,
    row: number,
    column: number
) => activeCell[0] === row && activeCell[1] === column;