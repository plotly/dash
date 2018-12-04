import * as R from 'ramda';
import React from 'react';

interface IAccumulator {
    cells: number;
    count: number;
}

function renderFragment(cells: any[][] | null, offset: number = 0) {
    return cells ?
        (<table tabIndex={-1}>
            <tbody>
                {cells.map(
                    (row, idx) => <tr key={`row-${idx + offset}`}>{row}</tr>)
                }
            </tbody>
        </table>) :
        null;
}

export default (
    fixedColumns: number,
    fixedRows: number,
    cells: JSX.Element[][],
    offset: number
): (JSX.Element | null)[][] => {
    // slice out fixed columns
    const fixedColumnCells = fixedColumns ?
        R.map(row =>
            row.splice(0, R.reduceWhile<JSX.Element, IAccumulator>(
                acc => acc.count < fixedColumns,
                (acc, cell) => {
                    acc.cells++;
                    acc.count += (cell.props.colSpan || 1);

                    return acc;
                },
                { cells: 0, count: 0 },
                row as any
            ).cells),
            cells) :
        null;

    // slice out fixed rows
    const fixedRowCells = fixedRows ?
        cells.splice(0, fixedRows) :
        null;

    const fixedRowAndColumnCells = fixedRows && fixedColumnCells ?
        fixedColumnCells.splice(0, fixedRows) :
        null;

    return [
        [renderFragment(fixedRowAndColumnCells), renderFragment(fixedRowCells)],
        [renderFragment(fixedColumnCells), renderFragment(cells, offset)]
    ];
};