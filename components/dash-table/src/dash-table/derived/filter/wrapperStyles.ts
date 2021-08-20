import * as R from 'ramda';

import {memoizeOneFactory} from 'core/memoizer';

import {Columns} from 'dash-table/components/Table/props';

import {
    IConvertedStyle,
    getFilterCellStyle,
    getFilterOpCellStyle
} from '../style';
import {traverseMap2} from 'core/math/matrixZipMap';

const getter = (columns: Columns, filterStyles: IConvertedStyle[]) =>
    R.map(column => getFilterCellStyle(column)(filterStyles), columns);

const opGetter = (
    rows: number,
    columns: number,
    columnStyles: IConvertedStyle[]
) =>
    traverseMap2(R.range(0, rows), R.range(0, columns), () =>
        getFilterOpCellStyle()(columnStyles)
    );

export default memoizeOneFactory(getter);
export const derivedFilterOpStyles = memoizeOneFactory(opGetter);
