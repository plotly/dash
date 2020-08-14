import * as R from 'ramda';

import {Columns} from 'dash-table/components/Table/props';

export default (
    columns: Columns,
    labels: any[][],
    mergeHeaders: boolean
): number[][] => {
    return R.map<any[], number[]>(rowLabels => {
        if (!mergeHeaders) {
            return R.range(0, columns.length);
        } else {
            const columnIndices = [0];
            let compareIndex = 0;
            rowLabels.forEach((label, i) => {
                if (label === rowLabels[compareIndex]) {
                    return;
                }
                columnIndices.push(i);
                compareIndex = i;
            });

            return columnIndices;
        }
    }, labels);
};
