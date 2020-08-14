import * as R from 'ramda';

import Environment from 'core/environment';
import {memoizeOneFactory} from 'core/memoizer';

import {IConvertedStyle} from '../style';
import {EdgesMatrices} from './type';
import {getFilterOpCellEdges} from '.';
import {traverse2} from 'core/math/matrixZipMap';

export default memoizeOneFactory(
    (
        columns: number,
        filter_action: boolean,
        styles: IConvertedStyle[],
        listViewStyle: boolean
    ) => {
        if (!filter_action || columns === 0) {
            return;
        }

        const edges = new EdgesMatrices(
            1,
            columns,
            Environment.defaultEdge,
            true,
            !listViewStyle
        );

        traverse2(R.range(0, 1), R.range(0, columns), (i, j) =>
            edges.setEdges(i, j, getFilterOpCellEdges()(styles))
        );

        return edges;
    }
);
