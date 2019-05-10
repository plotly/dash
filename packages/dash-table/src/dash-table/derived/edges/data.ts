import * as R from 'ramda';

import Environment from 'core/environment';
import { memoizeOneFactory } from 'core/memoizer';

import {
    IViewportOffset,
    IVisibleColumn,
    VisibleColumns,
    Data,
    ICellCoordinates
} from 'dash-table/components/Table/props';

import { IConvertedStyle } from '../style';
import { BorderStyle, BORDER_PROPERTIES, EdgesMatrices } from './type';

const getWeightedStyle = (
    borderStyles: IConvertedStyle[],
    column: IVisibleColumn,
    index: number,
    offset: IViewportOffset,
    datum: any
): BorderStyle => {
    const res: BorderStyle = {};

    R.addIndex<IConvertedStyle>(R.forEach)((rs, i) => {
        if (!rs.matchesColumn(column) ||
            !rs.matchesRow(index + offset.rows) ||
            !rs.matchesFilter(datum)
        ) {
            return;
        }

        R.forEach(p => {
            const s = rs.style[p] || rs.style.border;

            if (!R.isNil(s)) {
                res[p] = [s, i];
            }
        }, BORDER_PROPERTIES);
    }, borderStyles);

    return res;
};

export default memoizeOneFactory((
    columns: VisibleColumns,
    borderStyles: IConvertedStyle[],
    data: Data,
    offset: IViewportOffset,
    active_cell: ICellCoordinates | undefined,
    listViewStyle: boolean
) => {
    if (data.length === 0 || columns.length === 0) {
        return;
    }

    const edges = new EdgesMatrices(data.length, columns.length, Environment.defaultEdge, true, !listViewStyle);

    R.addIndex(R.forEach)((datum, i) =>
        R.addIndex<IVisibleColumn>(R.forEach)(
            (column, j) => {
                const cellStyle = getWeightedStyle(
                    borderStyles,
                    column,
                    i,
                    offset,
                    datum
                );

                edges.setEdges(i, j, cellStyle);
            },
            columns
        ),
        data
    );

    if (active_cell) {
        edges.setEdges(active_cell.row, active_cell.column, {
            borderBottom: [Environment.activeEdge, Infinity],
            borderLeft: [Environment.activeEdge, Infinity],
            borderRight: [Environment.activeEdge, Infinity],
            borderTop: [Environment.activeEdge, Infinity]
        });
    }

    return edges;
});