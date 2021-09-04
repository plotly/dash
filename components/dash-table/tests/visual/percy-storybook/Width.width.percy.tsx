import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';
import random from 'core/math/random';
import DataTable from 'dash-table/dash/DataTable';

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
    data
};

const props = Object.assign({}, baseProps, {
    columns: columns.map(id => ({id: id, name: id.toUpperCase(), width: 20}))
});

storiesOf('DashTable/Width width only', module)
    .add('without frozen columns or rows', () => <DataTable {...props} />)
    .add('with frozen rows', () => (
        <DataTable {...props} fixed_rows={{headers: true}} />
    ))
    .add('with frozen columns', () => (
        <DataTable {...props} fixed_columns={{headers: true}} />
    ))
    .add('with frozen rows and frozen columns', () => (
        <DataTable
            {...props}
            fixed_columns={{headers: true}}
            fixed_rows={{headers: true}}
        />
    ));
