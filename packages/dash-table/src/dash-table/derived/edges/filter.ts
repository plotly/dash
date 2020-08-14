import * as R from 'ramda';

import Environment from 'core/environment';
import {memoizeOneFactory} from 'core/memoizer';

import {Columns} from 'dash-table/components/Table/props';

import {IConvertedStyle} from '../style';
import {EdgesMatrices} from './type';
import {SingleColumnSyntaxTree} from 'dash-table/syntax-tree';
import {getFilterCellEdges} from '.';
import {traverse2} from 'core/math/matrixZipMap';

export default memoizeOneFactory(
    (
        columns: Columns,
        showFilters: boolean,
        map: Map<string, SingleColumnSyntaxTree>,
        styles: IConvertedStyle[],
        listViewStyle: boolean
    ) => {
        if (!showFilters || columns.length === 0) {
            return;
        }

        const edges = new EdgesMatrices(
            1,
            columns.length,
            Environment.defaultEdge,
            true,
            !listViewStyle
        );

        traverse2(R.range(0, 1), columns, (_, column, i, j) => {
            edges.setEdges(i, j, getFilterCellEdges(column)(styles));

            const ast = map.get(column.id.toString());
            if (ast && !ast.isValid) {
                edges.setEdges(i, j, {
                    borderBottom: [Environment.activeEdge, Infinity],
                    borderLeft: [Environment.activeEdge, Infinity],
                    borderRight: [Environment.activeEdge, Infinity],
                    borderTop: [Environment.activeEdge, Infinity]
                });
            }
        });

        return edges;
    }
);
