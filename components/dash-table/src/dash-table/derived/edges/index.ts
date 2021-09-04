import {BorderStyle, BORDER_PROPERTIES} from './type';
import {IConvertedStyle} from '../style';
import {Datum, IColumn} from 'dash-table/components/Table/props';
import {
    matchesDataCell,
    matchesDataOpCell,
    matchesFilterCell,
    getFilterOpStyles,
    matchesHeaderCell,
    getHeaderOpStyles
} from 'dash-table/conditional';
import {traverse2} from 'core/math/matrixZipMap';

function resolveEdges(
    styles: IConvertedStyle[],
    priority?: number
): BorderStyle {
    const res: BorderStyle = {};

    traverse2(styles, BORDER_PROPERTIES, (s, p, i) => {
        const border = s.style[p] || s.style.border;

        if (border) {
            res[p] = [border, priority ?? i];
        }
    });

    return res;
}

export const getDataCellEdges =
    (
        datum: Datum,
        i: number,
        column: IColumn,
        active: boolean,
        selected: boolean,
        priority?: number
    ) =>
    (styles: IConvertedStyle[]) =>
        resolveEdges(
            matchesDataCell(datum, i, column, active, selected)(styles),
            priority
        );
export const getDataOpCellEdges =
    (datum: Datum, i: number) => (styles: IConvertedStyle[]) =>
        resolveEdges(matchesDataOpCell(datum, i)(styles));
export const getFilterCellEdges =
    (column: IColumn) => (styles: IConvertedStyle[]) =>
        resolveEdges(matchesFilterCell(column)(styles));
export const getFilterOpCellEdges = () => (styles: IConvertedStyle[]) =>
    resolveEdges(getFilterOpStyles(styles));
export const getHeaderCellEdges =
    (i: number, column: IColumn) => (styles: IConvertedStyle[]) =>
        resolveEdges(matchesHeaderCell(i, column)(styles));
export const getHeaderOpCellEdges =
    (i: number) => (styles: IConvertedStyle[]) =>
        resolveEdges(getHeaderOpStyles(i)(styles));
