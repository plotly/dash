import {ICellCoordinates} from 'dash-table/components/Table/props';

export default (
    activeCell: ICellCoordinates | undefined,
    row: number,
    column: number
) => !!activeCell && activeCell.row === row && activeCell.column === column;
