import * as R from 'ramda';

import { VisibleColumns } from 'dash-table/components/Table/props';

export default (
    columns: VisibleColumns,
    labels: any[][],
    mergeHeaders: boolean
): number[][] => {
    return R.map(rowLabels => {
        if (!mergeHeaders) {
            return R.range(0, columns.length);
        } else {
            let columnIndices = [0];
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