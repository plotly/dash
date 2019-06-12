import * as R from 'ramda';
import React from 'react';
import { memoizeOneFactory } from 'core/memoizer';

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

const isEmpty = (cells: JSX.Element[][] | null) =>
    !cells ||
    cells.length === 0 ||
    cells[0].length === 0;

export default memoizeOneFactory((
    fixedColumns: number,
    fixedRows: number,
    cells: JSX.Element[][],
    offset: number
): { grid: (JSX.Element | null)[][], empty: boolean[][] } => {
    // slice out fixed columns
    let fixedColumnCells = fixedColumns ?
        R.map(row =>
            row.slice(0, R.reduceWhile<JSX.Element, IAccumulator>(
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

    cells = R.addIndex<JSX.Element[]>(R.map)((row, i) => row.slice(
        (fixedColumnCells && fixedColumnCells[i].length) || 0
    ), cells);

    // slice out fixed rows
    const fixedRowCells = fixedRows ?
        cells.slice(0, fixedRows) :
        null;

    cells = cells.slice(fixedRows);

    const fixedRowAndColumnCells = fixedRows && fixedColumnCells ?
        fixedColumnCells.slice(0, fixedRows) :
        null;

    fixedColumnCells = fixedColumnCells && fixedColumnCells.slice(fixedRows);

    return {
        grid: [
            [renderFragment(fixedRowAndColumnCells), renderFragment(fixedRowCells)],
            [renderFragment(fixedColumnCells), renderFragment(cells, offset)]
        ],
        empty: [
            [isEmpty(fixedRowAndColumnCells), isEmpty(fixedRowCells)],
            [isEmpty(fixedColumnCells), isEmpty(cells)]
        ]
    };
});