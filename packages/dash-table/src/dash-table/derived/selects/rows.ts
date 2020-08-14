import * as R from 'ramda';

import {Indices} from 'dash-table/components/Table/props';
import {memoizeOneFactory} from 'core/memoizer';

const getter = (indices: Indices, selectedRows: Indices): Indices => {
    const map = new Map<number, number>();

    R.addIndex<number>(R.forEach)((virtualIndex, index) => {
        map.set(virtualIndex, index);
    }, indices);

    const mappedSelectedRows: number[] = [];
    R.forEach(rowIndex => {
        const virtualIndex = map.get(rowIndex);

        if (virtualIndex !== undefined) {
            mappedSelectedRows.push(virtualIndex);
        }
    }, selectedRows);

    return mappedSelectedRows;
};

export default memoizeOneFactory(getter);
