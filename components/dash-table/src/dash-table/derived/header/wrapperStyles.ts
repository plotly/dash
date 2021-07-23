import * as R from 'ramda';

import {memoizeOneFactory} from 'core/memoizer';

import {Columns} from 'dash-table/components/Table/props';

import {
    IConvertedStyle,
    getHeaderCellStyle,
    getHeaderOpCellStyle
} from '../style';
import {traverseMap2} from 'core/math/matrixZipMap';

const getter = (
    columns: Columns,
    headerRows: number,
    headerStyles: IConvertedStyle[]
) =>
    traverseMap2(R.range(0, headerRows), columns, (i, column) =>
        getHeaderCellStyle(i, column)(headerStyles)
    );

const opGetter = (
    rows: number,
    columns: number,
    columnStyles: IConvertedStyle[]
) =>
    traverseMap2(R.range(0, rows), R.range(0, columns), i =>
        getHeaderOpCellStyle(i)(columnStyles)
    );

export default memoizeOneFactory(getter);
export const derivedHeaderOpStyles = memoizeOneFactory(opGetter);
