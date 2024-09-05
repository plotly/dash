import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';

import random from 'core/math/random';
import DataTable from 'dash-table/dash/DataTable';
import {TableAction} from 'dash-table/components/Table/props';

const setProps = () => {};

const columns = ['a', 'b', 'c'];

const data = (() => {
    const r = random(1);

    return R.range(0, 5).map(() =>
        ['a', 'b', 'c'].reduce((obj: any, key) => {
            obj[key] = Math.floor(r() * 1000);
            return obj;
        }, {})
    );
})();

const baseProps = {
    setProps,
    fill_width: false,
    id: 'table',
    data,
    filter_action: TableAction.Native,
    style_cell: {width: 100, max_width: 100, min_width: 100}
};

const props = Object.assign({}, baseProps, {
    columns: columns.map(id => ({id: id, name: id.toUpperCase()}))
});

storiesOf('DashTable/Empty', module).add('all variants', () => (
    <div>
        <div>with column filters -- no query</div>
        <DataTable {...props} />
        <div>with column filters -- invalid query</div>
        <DataTable
            {...R.mergeRight(props, {
                filter_query: '{a} !'
            })}
        />
        <div>with column filters -- single query</div>
        <DataTable
            {...R.mergeRight(props, {
                filter_query: '{a} ge 0'
            })}
        />
        <div>with column filters -- multi query</div>
        <DataTable
            {...R.mergeRight(props, {
                filter_query: '{a} ge 0 && {b} ge 0'
            })}
        />
        <div>with column filters -- multi query, no data</div>
        <DataTable
            {...R.mergeRight(props, {
                filter_query: '{a} gt 1000 && {b} gt 1000'
            })}
        />
    </div>
));
