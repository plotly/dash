import Environment from 'core/environment';
import { memoizeOneFactory } from 'core/memoizer';

import {
    IViewportOffset,
    Columns,
    Data,
    ICellCoordinates
} from 'dash-table/components/Table/props';

import { IConvertedStyle } from '../style';
import { EdgesMatrices } from './type';
import { getDataCellEdges } from '.';
import { traverse2 } from 'core/math/matrixZipMap';

export default memoizeOneFactory((
    columns: Columns,
    styles: IConvertedStyle[],
    data: Data,
    offset: IViewportOffset,
    active_cell: ICellCoordinates | undefined,
    listViewStyle: boolean
) => {
    if (data.length === 0 || columns.length === 0) {
        return;
    }

    const edges = new EdgesMatrices(data.length, columns.length, Environment.defaultEdge, true, !listViewStyle);

    traverse2(
        data,
        columns,
        (datum, column, i, j) => edges.setEdges(i, j, getDataCellEdges(datum, i + offset.rows, column)(styles))
    );

    if (active_cell) {
        edges.setEdges(active_cell.row - offset.rows, active_cell.column - offset.columns, {
            borderBottom: [Environment.activeEdge, Infinity],
            borderLeft: [Environment.activeEdge, Infinity],
            borderRight: [Environment.activeEdge, Infinity],
            borderTop: [Environment.activeEdge, Infinity]
        });
    }

    return edges;
});