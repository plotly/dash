import {map, range, xprod} from 'ramda';
import {
    ICellCoordinates,
    Columns,
    IDerivedData,
    IndexedData
} from 'dash-table/components/Table/props';

export function makeCell(
    row: number,
    column: number,
    columns: Columns,
    viewport: IDerivedData
) {
    const cell: ICellCoordinates = {
        row,
        column,
        column_id: columns[column].id
    };
    const rowId = (viewport.data as IndexedData)[row].id;
    if (rowId !== undefined) {
        cell.row_id = rowId;
    }
    return cell;
}

interface ISelectionBounds {
    minRow: number;
    maxRow: number;
    minCol: number;
    maxCol: number;
}

export function makeSelection(
    bounds: ISelectionBounds,
    columns: Columns,
    viewport: IDerivedData
) {
    const {minRow, maxRow, minCol, maxCol} = bounds;
    return map(
        rc =>
            makeCell(
                (rc as number[])[0],
                (rc as number[])[1],
                columns,
                viewport
            ),
        xprod(range(minRow, maxRow + 1), range(minCol, maxCol + 1))
    );
}
