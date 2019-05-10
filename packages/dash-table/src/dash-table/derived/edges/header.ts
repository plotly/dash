import * as R from 'ramda';

import Environment from 'core/environment';
import { memoizeOneFactory } from 'core/memoizer';

import {
    IVisibleColumn,
    VisibleColumns
} from 'dash-table/components/Table/props';

import { IConvertedStyle } from '../style';
import { BorderStyle, BORDER_PROPERTIES, EdgesMatrices } from './type';

const getWeightedStyle = (
    borderStyles: IConvertedStyle[],
    column: IVisibleColumn,
    index: number
): BorderStyle => {
    const res: BorderStyle = {};

    R.addIndex<IConvertedStyle>(R.forEach)((rs, i) => {
        if (!rs.matchesColumn(column) ||
            !rs.matchesRow(index)
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
    headerRows: number,
    borderStyles: IConvertedStyle[],
    listViewStyle: boolean
) => {
    if (headerRows === 0 || columns.length === 0) {
        return;
    }

    const edges = new EdgesMatrices(headerRows, columns.length, Environment.defaultEdge, true, !listViewStyle);

    R.forEach(i =>
        R.addIndex<IVisibleColumn>(R.forEach)(
            (column, j) => {
                const cellStyle = getWeightedStyle(
                    borderStyles,
                    column,
                    i
                );

                edges.setEdges(i, j, cellStyle);
            },
            columns
        ),
        R.range(0, headerRows)
    );

    return edges;
});