import * as R from 'ramda';

import Environment from 'core/environment';
import { memoizeOneFactory } from 'core/memoizer';

import {
    IVisibleColumn,
    VisibleColumns
} from 'dash-table/components/Table/props';

import { IConvertedStyle } from '../style';
import { BorderStyle, BORDER_PROPERTIES, EdgesMatrices } from './type';
import { SingleColumnSyntaxTree } from 'dash-table/syntax-tree';

const getWeightedStyle = (
    borderStyles: IConvertedStyle[],
    column: IVisibleColumn
): BorderStyle => {
    const res: BorderStyle = {};

    R.addIndex<IConvertedStyle>(R.forEach)((rs, i) => {
        if (!rs.matchesColumn(column)) {
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
    showFilters: boolean,
    map: Map<string, SingleColumnSyntaxTree>,
    borderStyles: IConvertedStyle[],
    listViewStyle: boolean
) => {
    if (!showFilters || columns.length === 0) {
        return;
    }

    const edges = new EdgesMatrices(1, columns.length, Environment.defaultEdge, true, !listViewStyle);

    R.forEach(i =>
        R.addIndex<IVisibleColumn>(R.forEach)(
            (column, j) => {
                const cellStyle = getWeightedStyle(
                    borderStyles,
                    column
                );

                edges.setEdges(i, j, cellStyle);

                const ast = map.get(column.id.toString());
                if (ast && !ast.isValid) {
                    edges.setEdges(i, j, {
                        borderBottom: [Environment.activeEdge, Infinity],
                        borderLeft: [Environment.activeEdge, Infinity],
                        borderRight: [Environment.activeEdge, Infinity],
                        borderTop: [Environment.activeEdge, Infinity]
                    });
                }
            },
            columns
        ),
        R.range(0, 1)
    );

    return edges;
});