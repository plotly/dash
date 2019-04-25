import * as R from 'ramda';
import { CSSProperties } from 'react';

import { memoizeOneFactory } from 'core/memoizer';

import { VisibleColumns } from 'dash-table/components/Table/props';

import { IConvertedStyle } from '../style';

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

        return relevantStyles.length ? R.mergeAll(relevantStyles) : undefined;
    }, columns);
}

export default memoizeOneFactory(getter);
