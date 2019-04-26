import * as R from 'ramda';

export function selectionBounds(selected_cells) {
    const selectedRows = R.pluck('row', selected_cells);
    const selectedCols = R.pluck('column', selected_cells);

    return {
        minRow: R.reduce(R.min, Infinity, selectedRows),
        minCol: R.reduce(R.min, Infinity, selectedCols),
        maxRow: R.reduce(R.max, 0, selectedRows),
        maxCol: R.reduce(R.max, 0, selectedCols)
    };
}

export function selectionCycle(nextCell, selected_cells) {
    const {minRow, minCol, maxRow, maxCol} = selectionBounds(selected_cells);

    const [nextRow, nextCol] = nextCell;
    const adjustedCell = [nextRow, nextCol];

    if (nextRow > maxRow) {
        // wrap back to first row
        adjustedCell[0] = minRow;

        // try and increment column
        if (nextCol + 1 > maxCol) {
            adjustedCell[1] = minCol;
        } else {
            adjustedCell[1] = nextCol + 1;
        }
    }

    if (nextRow < minRow) {
        // wrap to last row
        adjustedCell[0] = maxRow;

        // try and decrement column
        if (nextCol - 1 < minCol) {
            adjustedCell[1] = maxCol;
        } else {
            adjustedCell[1] = nextCol - 1;
        }
    }

    if (nextCol > maxCol) {
        // wrap back to first column
        adjustedCell[1] = minCol;

        // try and increment row
        if (nextRow + 1 > maxRow) {
            adjustedCell[0] = minRow;
        } else {
            adjustedCell[0] = nextRow + 1;
        }
    }

    if (nextCol < minCol) {
        // wrap back to last column
        adjustedCell[1] = maxCol;

        // try and decrement row
        if (nextRow - 1 < minCol) {
            adjustedCell[0] = maxRow;
        } else {
            adjustedCell[0] = nextRow - 1;
        }
    }

    return adjustedCell;
}
