import * as R from 'ramda';

import Environment from 'core/environment';
import { memoizeOneFactory } from 'core/memoizer';

import { IConvertedStyle } from '../style';
import { BorderStyle, BORDER_PROPERTIES, EdgesMatrices } from './type';

const getWeightedStyle = (
    borderStyles: IConvertedStyle[],
    index: number
): BorderStyle => {
    const res: BorderStyle = {};

    R.addIndex<IConvertedStyle>(R.forEach)((rs, i) => {
        if (rs.checksColumn() ||
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
    columns: number,
    headerRows: number,
    borderStyles: IConvertedStyle[],
    listViewStyle: boolean
) => {
    if (headerRows === 0 || columns === 0) {
        return;
    }

    const edges = new EdgesMatrices(headerRows, columns, Environment.defaultEdge, true, !listViewStyle);

    R.forEach(i =>
        R.forEach(j => {
            const cellStyle = getWeightedStyle(
                borderStyles,
                i
            );

            edges.setEdges(i, j, cellStyle);
        },
            R.range(0, columns)
        ),
        R.range(0, headerRows)
    );

    return edges;
});