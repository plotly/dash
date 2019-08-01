import * as R from 'ramda';
import { CSSProperties } from 'react';

import { memoizeOneFactory } from 'core/memoizer';
import { Data, Columns, IViewportOffset, SelectedCells } from 'dash-table/components/Table/props';
import { IConvertedStyle, getDataCellStyle, getDataOpCellStyle } from '../style';
import { traverseMap2, shallowClone } from 'core/math/matrixZipMap';

const SELECTED_CELL_STYLE = { backgroundColor: 'var(--selected-background)' };

const partialGetter = (
    columns: Columns,
    styles: IConvertedStyle[],
    data: Data,
    offset: IViewportOffset
) => traverseMap2(
    data,
    columns,
    (datum, column, i) => getDataCellStyle(datum, i + offset.rows, column)(styles)
);

const getter = (
    styles: CSSProperties[][],
    offset: IViewportOffset,
    selectedCells: SelectedCells
) => {
    styles = shallowClone(styles);

    R.forEach(({ row: i, column: j }) => {
        i -= offset.rows;
        j -= offset.columns;

        if (i < 0 || j < 0 || styles.length <= i || styles[i].length <= j) {
            return;
        }

        styles[i][j] = R.merge(styles[i][j], SELECTED_CELL_STYLE);
    }, selectedCells);

    return styles;
};

const opGetter = (
    columns: number,
    styles: IConvertedStyle[],
    data: Data,
    offset: IViewportOffset
) => traverseMap2(
    data,
    R.range(0, columns),
    (datum, _, i) => getDataOpCellStyle(datum, i + offset.rows)(styles)
);

export const derivedPartialDataStyles = memoizeOneFactory(partialGetter);
export const derivedDataStyles = memoizeOneFactory(getter);
export const derivedDataOpStyles = memoizeOneFactory(opGetter);