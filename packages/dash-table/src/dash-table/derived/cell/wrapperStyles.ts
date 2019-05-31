import * as R from 'ramda';
import { CSSProperties } from 'react';

import { memoizeOneFactory } from 'core/memoizer';
import { Data, VisibleColumns, IViewportOffset, SelectedCells, ICellCoordinates } from 'dash-table/components/Table/props';
import { IConvertedStyle } from '../style';
import { BORDER_PROPERTIES_AND_FRAGMENTS } from '../edges/type';

type Style = CSSProperties | undefined;

function getter(
    columns: VisibleColumns,
    columnStyles: IConvertedStyle[],
    data: Data,
    offset: IViewportOffset,
    selectedCells: SelectedCells
): Style[][] {
    return R.addIndex<any, Style[]>(R.map)((datum, index) => R.addIndex<any, Style>(R.map)((column, columnIndex) => {
        const relevantStyles = R.map(
            s => s.style,
            R.filter<IConvertedStyle>(
                style =>
                    style.matchesColumn(column) &&
                    style.matchesRow(index + offset.rows) &&
                    style.matchesFilter(datum),
                columnStyles
            )
        );
        const matchCell = (cell: ICellCoordinates) => cell.row === index && cell.column === columnIndex;
        const isSelectedCell: boolean = R.any(matchCell)(selectedCells);
        if (isSelectedCell) {
            relevantStyles.push({backgroundColor:  'var(--selected-background)'});
        }
        return relevantStyles.length ?
            R.omit(
                BORDER_PROPERTIES_AND_FRAGMENTS,
                R.mergeAll(relevantStyles)
            ) :
            undefined;
    }, columns), data);
}

function opGetter(
    columns: number,
    columnStyles: IConvertedStyle[],
    data: Data,
    offset: IViewportOffset
) {
    return R.addIndex<any, Style[]>(R.map)((datum, index) => R.map(_ => {
        const relevantStyles = R.map(
            s => s.style,
            R.filter<IConvertedStyle>(
                style =>
                    !style.checksColumn() &&
                    style.matchesRow(index + offset.rows) &&
                    style.matchesFilter(datum),
                columnStyles
            )
        );

        return relevantStyles.length ?
            R.omit(
                BORDER_PROPERTIES_AND_FRAGMENTS,
                R.mergeAll(relevantStyles)
            ) :
            undefined;
    }, R.range(0, columns)), data);
}

export default memoizeOneFactory(getter);
export const derivedDataOpStyles = memoizeOneFactory(opGetter);