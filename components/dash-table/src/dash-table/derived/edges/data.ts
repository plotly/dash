import Environment from 'core/environment';
import {memoizeOneFactory} from 'core/memoizer';

import {
    IViewportOffset,
    Columns,
    Data,
    ICellCoordinates,
    SelectedCells
} from 'dash-table/components/Table/props';

import isActiveCell from 'dash-table/derived/cell/isActive';

import {IConvertedStyle} from '../style';
import {EdgesMatrices, BorderStyle} from './type';
import {getDataCellEdges} from '.';
import {traverse2} from 'core/math/matrixZipMap';

const ACTIVE_PRIORITY = Number.MAX_SAFE_INTEGER;
const SELECTED_PRIORITY = Number.MAX_SAFE_INTEGER - 1;

const partialGetter = (
    columns: Columns,
    styles: IConvertedStyle[],
    data: Data,
    offset: IViewportOffset,
    listViewStyle: boolean
) => {
    if (data.length === 0 || columns.length === 0) {
        return;
    }

    const edges = new EdgesMatrices(
        data.length,
        columns.length,
        Environment.defaultEdge,
        true,
        !listViewStyle
    );

    traverse2(data, columns, (datum, column, i, j) =>
        edges.setEdges(
            i,
            j,
            getDataCellEdges(
                datum,
                i + offset.rows,
                column,
                false,
                false
            )(styles)
        )
    );

    return edges;
};

const getter = (
    baseline: EdgesMatrices | undefined,
    columns: Columns,
    styles: IConvertedStyle[],
    data: Data,
    offset: IViewportOffset,
    activeCell: ICellCoordinates | undefined,
    selectedCells: SelectedCells
) => {
    if (!baseline) {
        return baseline;
    }

    const edges = baseline.clone();

    const cells = selectedCells.length
        ? selectedCells
        : activeCell
        ? [activeCell]
        : [];

    const inactiveStyles = styles.filter(style => !style.checksState());
    const selectedStyles = styles.filter(style => style.checksStateSelected());
    const activeStyles = styles.filter(style => style.checksStateActive());

    cells.forEach(({row: i, column: j}) => {
        const iWithOffset = i - offset.rows;
        const jWithOffset = j - offset.columns;

        if (iWithOffset < 0 || jWithOffset < 0 || data.length <= iWithOffset) {
            return;
        }

        const active = isActiveCell(activeCell, i, j);

        const priority = active ? ACTIVE_PRIORITY : SELECTED_PRIORITY;
        const defaultEdge = active
            ? Environment.activeEdge
            : Environment.defaultEdge;

        const style: BorderStyle = {
            ...getDataCellEdges(
                data[iWithOffset],
                iWithOffset,
                columns[j],
                active,
                true,
                priority
            )(inactiveStyles),

            borderBottom: [defaultEdge, priority],
            borderLeft: [defaultEdge, priority],
            borderRight: [defaultEdge, priority],
            borderTop: [defaultEdge, priority],

            ...getDataCellEdges(
                data[iWithOffset],
                iWithOffset,
                columns[j],
                active,
                true,
                priority
            )(selectedStyles),
            ...getDataCellEdges(
                data[iWithOffset],
                iWithOffset,
                columns[j],
                active,
                true,
                priority
            )(activeStyles)
        };

        edges.setEdges(iWithOffset, j, style);
    });

    return edges;
};

export const derivedPartialDataEdges = memoizeOneFactory(partialGetter);
export const derivedDataEdges = memoizeOneFactory(getter);
