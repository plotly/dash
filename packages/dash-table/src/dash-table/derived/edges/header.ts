import * as R from 'ramda';

import Environment from 'core/environment';
import {memoizeOneFactory} from 'core/memoizer';

import {Columns} from 'dash-table/components/Table/props';

import {IConvertedStyle} from '../style';
import {EdgesMatrices} from './type';
import {getHeaderCellEdges} from '.';
import {traverse2} from 'core/math/matrixZipMap';

export default memoizeOneFactory(
    (
        columns: Columns,
        headerRows: number,
        styles: IConvertedStyle[],
        listViewStyle: boolean
    ) => {
        if (headerRows === 0 || columns.length === 0) {
            return;
        }

        const edges = new EdgesMatrices(
            headerRows,
            columns.length,
            Environment.defaultEdge,
            true,
            !listViewStyle
        );

        traverse2(R.range(0, headerRows), columns, (_, column, i, j) =>
            edges.setEdges(i, j, getHeaderCellEdges(i, column)(styles))
        );

        return edges;
    }
);
