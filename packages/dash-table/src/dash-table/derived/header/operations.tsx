import * as R from 'ramda';
import React from 'react';

import {memoizeOneFactory} from 'core/memoizer';

import {Selection} from 'dash-table/components/Table/props';

function rowSelectCell() {
    return (
        <th
            key='select'
            className='expanded-row--empty-cell dash-select-header'
            style={{width: '30px', maxWidth: '30px', minWidth: '30px'}}
        />
    );
}

function rowDeleteHeader() {
    return (
        <th
            key='delete'
            className='expanded-row--empty-cell dash-delete-header'
            style={{width: '30px', maxWidth: '30px', minWidth: '30px'}}
        />
    );
}

const getter = (
    headerRows: number,
    rowSelectable: Selection,
    rowDeletable: boolean
): JSX.Element[][] =>
    R.addIndex<number, JSX.Element[]>(R.map)(
        () => [
            ...(rowDeletable ? [rowDeleteHeader()] : []),
            ...(rowSelectable ? [rowSelectCell()] : [])
        ],
        R.range(0, headerRows)
    );

export default memoizeOneFactory(getter);
