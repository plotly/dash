import * as R from 'ramda';

import {memoizeOneFactory} from 'core/memoizer';

import getHeaderRows from 'dash-table/derived/header/headerRows';
import getIndices from 'dash-table/derived/header/indices';
import getLabels from 'dash-table/derived/header/labels';

import {Columns} from 'dash-table/components/Table/props';

export default memoizeOneFactory(
    (
        columns: Columns,
        usedColumns: Columns,
        merge_duplicate_headers: boolean
    ) => {
        const headerRows = getHeaderRows(columns);

        const labels = getLabels(usedColumns, headerRows);
        const indices = getIndices(
            usedColumns,
            labels,
            merge_duplicate_headers
        );

        return R.zip(labels, indices);
    }
);
