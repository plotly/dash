import * as R from 'ramda';

import Environment from 'core/environment';
import { memoizeOneFactory } from 'core/memoizer';

import { IConvertedStyle } from '../style';
import { BorderStyle, BORDER_PROPERTIES, EdgesMatrices } from './type';

const getWeightedStyle = (
    borderStyles: IConvertedStyle[]
): BorderStyle => {
    const res: BorderStyle = {};

    R.addIndex<IConvertedStyle>(R.forEach)((rs, i) => {
        if (rs.checksColumn()) {
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
    filter_action: boolean,
    borderStyles: IConvertedStyle[],
    listViewStyle: boolean
) => {
    if (!filter_action || columns === 0) {
        return;
    }

    const edges = new EdgesMatrices(1, columns, Environment.defaultEdge, true, !listViewStyle);

    R.forEach(i =>
        R.forEach(j => {
            const cellStyle = getWeightedStyle(borderStyles);

            edges.setEdges(i, j, cellStyle);
        },
            R.range(0, columns)
        ),
        R.range(0, 1)
    );

    return edges;
});