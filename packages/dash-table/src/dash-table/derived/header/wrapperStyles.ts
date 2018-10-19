import * as R from 'ramda';
import { CSSProperties } from 'react';

import { memoizeOneFactory } from 'core/memoizer';

import { VisibleColumns } from 'dash-table/components/Table/props';

import { IConvertedStyle } from '../style';

type Style = CSSProperties | undefined;

function getter(
    columns: VisibleColumns,
    headerRows: number,
    headerStyles: IConvertedStyle[]
): Style[][] {
    return R.map(idx => R.map(column => {
        const relevantStyles = R.map(
            s => s.style,
            R.filter(
                style =>
                    style.matchesColumn(column) &&
                    style.matchesRow(idx),
                headerStyles
            )
        );

        return relevantStyles.length ? R.mergeAll(relevantStyles) : undefined;
    }, columns), R.range(0, headerRows));
}

export default memoizeOneFactory(getter);
