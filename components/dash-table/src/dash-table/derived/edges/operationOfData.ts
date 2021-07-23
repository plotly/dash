import * as R from 'ramda';

import Environment from 'core/environment';
import {memoizeOneFactory} from 'core/memoizer';

import {Data, IViewportOffset} from 'dash-table/components/Table/props';

import {IConvertedStyle} from '../style';
import {EdgesMatrices} from './type';
import {getDataOpCellEdges} from '.';
import {traverse2} from 'core/math/matrixZipMap';

export default memoizeOneFactory(
    (
        columns: number,
        styles: IConvertedStyle[],
        data: Data,
        offset: IViewportOffset,
        listViewStyle: boolean
    ) => {
        if (data.length === 0 || columns === 0) {
            return;
        }

        const edges = new EdgesMatrices(
            data.length,
            columns,
            Environment.defaultEdge,
            true,
            !listViewStyle
        );

        traverse2(data, R.range(0, columns), (datum, _, i, j) =>
            edges.setEdges(
                i,
                j,
                getDataOpCellEdges(datum, i + offset.rows)(styles)
            )
        );

        return edges;
    }
);
