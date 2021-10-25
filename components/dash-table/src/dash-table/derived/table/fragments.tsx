import * as R from 'ramda';
import React from 'react';
import {memoizeOneFactory} from 'core/memoizer';

interface IAccumulator {
    cells: number;
    count: number;
}

function renderFragment(cells: any[][] | null, offset = 0, fixedRows = 0) {
    return cells ? (
        <table className='cell-table' tabIndex={-1}>
            <tbody>
                {cells.map((row, idx) => {
                    const hidden = idx < fixedRows;
                    const content = hidden
                        ? row.map(r => getHidden(r, true))
                        : row;

                    return (
                        <tr
                            style={hidden ? {visibility: 'collapse'} : {}}
                            key={`row-${idx + offset}`}
                        >
                            {content}
                        </tr>
                    );
                })}
            </tbody>
        </table>
    ) : null;
}

const getHiddenCell = (cell: JSX.Element) => getHidden(cell);

const getHidden = (cell: JSX.Element, withContent = false) =>
    React.cloneElement(
        cell,
        {
            ...cell.props,
            className: cell.props.className
                ? `${cell.props.className} phantom-cell`
                : 'phantom-cell'
        },
        !withContent && (cell.type === 'th' || cell.type === 'td')
            ? null
            : cell.props.children
    );

const getFixedColSpan = (cell: JSX.Element, maxColSpan: number) =>
    React.cloneElement(cell, {
        ...cell.props,
        colSpan: R.isNil(cell.props.colSpan)
            ? cell.props.colSpan
            : Math.min(cell.props.colSpan, maxColSpan)
    });

const getLastOfType = (cell: JSX.Element) =>
    React.cloneElement(cell, {
        ...cell.props,
        className: cell.props.className
            ? `${cell.props.className} last-of-type`
            : 'last-of-type'
    });

const isEmpty = (cells: JSX.Element[][] | null) =>
    !cells || cells.length === 0 || cells[0].length === 0;

export default memoizeOneFactory(
    (
        fixedColumns: number,
        fixedRows: number,
        cells: JSX.Element[][],
        offset: number,
        shallowHeaders: JSX.Element[][]
    ): {grid: (JSX.Element | null)[][]; empty: boolean[][]} => {
        const getPivot = (row: JSX.Element[]) =>
            R.reduceWhile<JSX.Element, IAccumulator>(
                acc => acc.count < fixedColumns,
                (acc, cell) => {
                    acc.cells++;
                    acc.count += cell.props.colSpan || 1;

                    return acc;
                },
                {cells: 0, count: 0},
                row as any
            ).cells;

        // slice out fixed columns
        let fixedColumnCells = fixedColumns
            ? R.map(row => {
                  const pivot = getPivot(row);

                  const res = row
                      .slice(0, pivot)
                      .map((c, i) => getFixedColSpan(c, fixedColumns - i - 1))
                      .concat(row.slice(pivot).map(getHiddenCell));
                  res[pivot - 1] = getLastOfType(res[pivot - 1]);

                  return res;
              }, cells)
            : null;

        cells = R.isNil(fixedColumnCells)
            ? cells
            : R.map(row => {
                  const pivot = getPivot(row);

                  return row
                      .slice(0, pivot)
                      .map(getHiddenCell)
                      .concat(row.slice(pivot));
              }, cells);

        // slice out fixed rows
        const fixedRowCells = fixedRows ? cells.slice(0, fixedRows) : null;

        cells = cells.slice(shallowHeaders.length);
        cells = [...shallowHeaders, ...cells];

        const fixedRowAndColumnCells =
            fixedRows && fixedColumnCells
                ? fixedColumnCells.slice(0, fixedRows)
                : null;

        fixedColumnCells = fixedColumnCells || null;

        return {
            grid: [
                [
                    renderFragment(fixedRowAndColumnCells),
                    renderFragment(fixedRowCells)
                ],
                [
                    renderFragment(fixedColumnCells, 0, fixedRows),
                    renderFragment(cells, offset, fixedRows)
                ]
            ],
            empty: [
                [isEmpty(fixedRowAndColumnCells), isEmpty(fixedRowCells)],
                [isEmpty(fixedColumnCells), isEmpty(cells)]
            ]
        };
    }
);
