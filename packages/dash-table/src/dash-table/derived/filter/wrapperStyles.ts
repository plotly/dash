import * as R from 'ramda';
import { CSSProperties } from 'react';

import { memoizeOneFactory } from 'core/memoizer';

import { VisibleColumns } from 'dash-table/components/Table/props';

import { IConvertedStyle } from '../style';
import { BORDER_PROPERTIES_AND_FRAGMENTS } from '../edges/type';

type Style = CSSProperties | undefined;

function getter(
    columns: VisibleColumns,
    filterStyles: IConvertedStyle[]
): Style[] {
    return R.map(column => {
        const relevantStyles = R.map(
            s => s.style,
            R.filter<IConvertedStyle>(
                style => style.matchesColumn(column),
                filterStyles
            )
        );

        return relevantStyles.length ?
            R.omit(
                BORDER_PROPERTIES_AND_FRAGMENTS,
                R.mergeAll(relevantStyles)
            ) :
            undefined;
    }, columns);
}

function opGetter(
    rows: number,
    columns: number,
    columnStyles: IConvertedStyle[]
) {
    return R.map(() => R.map(() => {
        const relevantStyles = R.map(
            s => s.style,
            R.filter<IConvertedStyle>(
                style => !style.checksColumn(),
                columnStyles
            )
        );

        return relevantStyles.length ?
            R.omit(
                BORDER_PROPERTIES_AND_FRAGMENTS,
                R.mergeAll(relevantStyles)
            ) :
            undefined;
    }, R.range(0, columns)), R.range(0, rows));
}

export default memoizeOneFactory(getter);
export const derivedFilterOpStyles = memoizeOneFactory(opGetter);