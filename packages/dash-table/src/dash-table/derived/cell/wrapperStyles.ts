import * as R from 'ramda';
import { CSSProperties } from 'react';

import { memoizeOneFactory } from 'core/memoizer';
import { Data, VisibleColumns } from 'dash-table/components/Table/props';
import { IConvertedStyle } from '../style';

type Style = CSSProperties | undefined;

function getter(
    columns: VisibleColumns,
    columnStyles: IConvertedStyle[],
    data: Data
): Style[][] {
    return R.addIndex<any, Style[]>(R.map)((datum, index) => R.map(column => {
        const relevantStyles = R.map(
            s => s.style,
            R.filter(
                style =>
                    style.matchesColumn(column) &&
                    style.matchesRow(index) &&
                    style.matchesFilter(datum),
                columnStyles
            )
        );

        return relevantStyles.length ? R.mergeAll(relevantStyles) : undefined;
    }, columns), data);
}

export default memoizeOneFactory(getter);
