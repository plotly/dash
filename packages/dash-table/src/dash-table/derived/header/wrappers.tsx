import * as R from 'ramda';
import React from 'react';

import { memoizeOneFactory } from 'core/memoizer';

import { Columns } from 'dash-table/components/Table/props';

function getter(
    columns: Columns,
    labelsAndIndices: R.KeyValuePair<any[], number[]>[],
    mergeHeaders: boolean
): JSX.Element[][] {
    return R.map(([labels, indices]) => {
        return R.addIndex<number, JSX.Element>(R.map)(
            (columnIndex, index) => {
                const column = columns[columnIndex];

                let colSpan: number;
                if (!mergeHeaders) {
                    colSpan = 1;
                } else {
                    if (columnIndex === R.last(indices)) {
                        colSpan = labels.length - columnIndex;
                    } else {
                        colSpan = indices[index + 1] - columnIndex;
                    }
                }

                return (<th
                    key={`header-cell-${columnIndex}`}
                    data-dash-column={column.id}
                    colSpan={colSpan}
                    className={
                        `dash-header ` +
                        `column-${columnIndex} ` +
                        (columnIndex === columns.length - 1 || columnIndex === R.last(indices) ? 'cell--right-last ' : '')
                    }
                />);
            },
            indices
        );
    },
        labelsAndIndices
    );
}

export default memoizeOneFactory(getter);
