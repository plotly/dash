import * as R from 'ramda';
import {CSSProperties} from 'react';

import {memoizeOneFactory} from 'core/memoizer';
import {
    Data,
    Columns,
    IViewportOffset,
    SelectedCells,
    ICellCoordinates
} from 'dash-table/components/Table/props';
import {IConvertedStyle, getDataCellStyle, getDataOpCellStyle} from '../style';
import {traverseMap2, shallowClone} from 'core/math/matrixZipMap';

import isActiveCell from 'dash-table/derived/cell/isActive';
import Environment from 'core/environment';

const SELECTED_CELL_STYLE = {
    backgroundColor: Environment.supportsCssVariables
        ? 'var(--selected-background)'
        : 'rgba(255, 65, 54, 0.2)'
};

const partialGetter = (
    columns: Columns,
    styles: IConvertedStyle[],
    data: Data,
    offset: IViewportOffset
) =>
    traverseMap2(data, columns, (datum, column, i) =>
        getDataCellStyle(datum, i + offset.rows, column, false, false)(styles)
    );

const getter = (
    baseline: CSSProperties[][],
    columns: Columns,
    styles: IConvertedStyle[],
    data: Data,
    offset: IViewportOffset,
    activeCell: ICellCoordinates | undefined,
    selectedCells: SelectedCells
) => {
    baseline = shallowClone(baseline);

    const cells = selectedCells.length
        ? selectedCells
        : activeCell
        ? [activeCell]
        : [];

    const inactiveStyles = styles.filter(style => !style.checksState());
    const selectedStyles = styles.filter(style => style.checksStateSelected());
    const activeStyles = styles.filter(style => style.checksStateActive());

    cells.forEach(({row: i, column: j}) => {
        const iNoOffset = i - offset.rows;
        const jNoOffset = j - offset.columns;

        if (
            iNoOffset < 0 ||
            jNoOffset < 0 ||
            baseline.length <= iNoOffset ||
            baseline[iNoOffset].length <= jNoOffset
        ) {
            return;
        }

        const active = isActiveCell(activeCell, i, j);

        const style = {
            ...getDataCellStyle(
                data[i],
                i + offset.rows,
                columns[j],
                active,
                true
            )(inactiveStyles),
            ...SELECTED_CELL_STYLE,
            ...getDataCellStyle(
                data[i],
                i + offset.rows,
                columns[j],
                active,
                true
            )(selectedStyles),
            ...getDataCellStyle(
                data[i],
                i + offset.rows,
                columns[j],
                active,
                true
            )(activeStyles)
        };

        baseline[iNoOffset][jNoOffset] = style;
    });

    return baseline;
};

const opGetter = (
    columns: number,
    styles: IConvertedStyle[],
    data: Data,
    offset: IViewportOffset
) =>
    traverseMap2(data, R.range(0, columns), (datum, _, i) =>
        getDataOpCellStyle(datum, i + offset.rows)(styles)
    );

export const derivedPartialDataStyles = memoizeOneFactory(partialGetter);
export const derivedDataStyles = memoizeOneFactory(getter);
export const derivedDataOpStyles = memoizeOneFactory(opGetter);
