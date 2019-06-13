import { BorderStyle, BORDER_PROPERTIES } from './type';
import { IConvertedStyle } from '../style';
import { Datum, IVisibleColumn } from 'dash-table/components/Table/props';
import { matchesDataCell, matchesDataOpCell, matchesFilterCell, getFilterOpStyles, matchesHeaderCell, getHeaderOpStyles } from 'dash-table/conditional';
import { traverse2 } from 'core/math/matrixZipMap';

function resolveEdges(styles: IConvertedStyle[]): BorderStyle {
    let res: BorderStyle = {};

    traverse2(
        styles,
        BORDER_PROPERTIES,
        (s, p, i) => {
            const border = s.style[p] || s.style.border;

            if (border) {
                res[p] = [border, i];
            }
        }
    );

    return res;
}

export const getDataCellEdges = (datum: Datum, i: number, column: IVisibleColumn) => (styles: IConvertedStyle[]) => resolveEdges(matchesDataCell(datum, i, column)(styles));
export const getDataOpCellEdges = (datum: Datum, i: number) => (styles: IConvertedStyle[]) => resolveEdges(matchesDataOpCell(datum, i)(styles));
export const getFilterCellEdges = (column: IVisibleColumn) => (styles: IConvertedStyle[]) => resolveEdges(matchesFilterCell(column)(styles));
export const getFilterOpCellEdges = () => (styles: IConvertedStyle[]) => resolveEdges(getFilterOpStyles(styles));
export const getHeaderCellEdges = (i: number, column: IVisibleColumn) => (styles: IConvertedStyle[]) => resolveEdges(matchesHeaderCell(i, column)(styles));
export const getHeaderOpCellEdges = (i: number) => (styles: IConvertedStyle[]) => resolveEdges(getHeaderOpStyles(i)(styles));