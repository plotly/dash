import * as R from 'ramda';

import { BorderStyle, BORDER_PROPERTIES } from './type';
import { IConvertedStyle } from '../style';
import { Datum, IVisibleColumn } from 'dash-table/components/Table/props';
import { matchesDataCell, matchesDataOpCell, matchesFilterCell, getFilterOpStyles, matchesHeaderCell, getHeaderOpStyles } from 'dash-table/conditional';

function resolveEdges(styles: IConvertedStyle[]): BorderStyle {
    let res: BorderStyle = {};

    R.addIndex<IConvertedStyle>(R.forEach)((s, i) => R.forEach(p => {
        const border = s.style[p] || s.style.border;

        if (border) {
            res[p] = [border, i];
        }
    }, BORDER_PROPERTIES), styles);

    return res;
}

export const getDataCellEdges = (datum: Datum, i: number, column: IVisibleColumn) => R.compose(resolveEdges, matchesDataCell(datum, i, column));
export const getDataOpCellEdges = (datum: Datum, i: number) => R.compose(resolveEdges, matchesDataOpCell(datum, i));
export const getFilterCellEdges = (column: IVisibleColumn) => R.compose(resolveEdges, matchesFilterCell(column));
export const getFilterOpCellEdges = () => R.compose(resolveEdges, getFilterOpStyles);
export const getHeaderCellEdges = (i: number, column: IVisibleColumn) => R.compose(resolveEdges, matchesHeaderCell(i, column));
export const getHeaderOpCellEdges = (i: number) => R.compose(resolveEdges, getHeaderOpStyles(i));