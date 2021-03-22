import * as R from 'ramda';
import React from 'react';

import {memoizeOneFactory} from 'core/memoizer';
import {clearSelection} from 'dash-table/utils/actions';

import {
    Data,
    Datum,
    SetProps,
    Selection,
    Indices
} from 'dash-table/components/Table/props';

function deleteRow(idx: number, data: Data, selectedRows: number[]) {
    const newProps: any = {
        data: R.remove(idx, 1, data),
        // We could try to adjust selection, but there are lots of edge cases
        ...clearSelection
    };

    if (R.is(Array, selectedRows) && R.any(i => i >= idx, selectedRows)) {
        newProps.selected_rows = R.map(
            // all rows past idx have now lost one from their index
            (i: number) => (i > idx ? i - 1 : i),
            R.without([idx], selectedRows)
        );
        newProps.selected_row_ids = R.map(
            i => newProps.data[i].id,
            newProps.selected_rows
        );
    }
    return newProps;
}

function rowSelectCell(
    id: string,
    idx: number,
    rowSelectable: Selection,
    selectedRows: number[],
    setProps: SetProps,
    data: Data
) {
    return (
        <td
            key='select'
            className='dash-select-cell'
            style={{
                width: '30px',
                maxWidth: '30px',
                minWidth: '30px',
                textAlign: 'center'
            }}
        >
            <input
                type={rowSelectable === 'single' ? 'radio' : 'checkbox'}
                style={{verticalAlign: 'middle'}}
                name={`row-select-${id}`}
                checked={R.includes(idx, selectedRows)}
                onChange={() => {
                    const newSelectedRows =
                        rowSelectable === 'single'
                            ? [idx]
                            : R.ifElse(
                                  R.includes(idx),
                                  R.without([idx]),
                                  R.append(idx)
                              )(selectedRows);
                    setProps({
                        selected_rows: newSelectedRows,
                        selected_row_ids: R.map(
                            i => data[i].id,
                            newSelectedRows
                        )
                    });
                }}
            />
        </td>
    );
}

function rowDeleteCell(doDelete: () => any) {
    return (
        <td
            key='delete'
            className='dash-delete-cell'
            onClick={() => doDelete()}
            style={{width: '30px', maxWidth: '30px', minWidth: '30px'}}
        >
            {'×'}
        </td>
    );
}

const getter = (
    id: string,
    data: Data,
    viewportData: Data,
    viewportIndices: Indices,
    rowSelectable: Selection,
    rowDeletable: boolean,
    selectedRows: number[],
    setProps: SetProps
): JSX.Element[][] =>
    R.addIndex<Datum, JSX.Element[]>(R.map)(
        (_, rowIndex) => [
            ...(rowDeletable
                ? [
                      rowDeleteCell(() =>
                          setProps(
                              deleteRow(
                                  viewportIndices[rowIndex],
                                  data,
                                  selectedRows
                              )
                          )
                      )
                  ]
                : []),
            ...(rowSelectable
                ? [
                      rowSelectCell(
                          id,
                          viewportIndices[rowIndex],
                          rowSelectable,
                          selectedRows,
                          setProps,
                          data
                      )
                  ]
                : [])
        ],
        viewportData
    );

export default memoizeOneFactory(getter);
