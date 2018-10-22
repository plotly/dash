import * as R from 'ramda';
import React from 'react';
import { storiesOf } from '@storybook/react';
import random from 'core/math/random';
import DashTable from 'dash-table/Table';

const setProps = () => { };

const columns = ['a', 'b', 'c']
    .map(id => ({ id: id, name: id.toUpperCase() }));

const data = (() => {
    const r = random(1);

    return R.range(0, 5).map(() => (
        ['a', 'b', 'c'].reduce((obj: any, key) => {
            obj[key] = Math.floor(r() * 1000);
            return obj;
        }, {})
    ));
})();

const columns2 = ['a', 'b', 'c', 'd', 'e', 'f']
    .map(id => ({ id: id, name: id.toUpperCase() }));

const data2 = (() => {
    const r = random(1);

    return R.range(0, 50).map(() => (
        ['a', 'b', 'c', 'd', 'e', 'f'].reduce((obj: any, key) => {
            obj[key] = Math.floor(r() * 1000);
            return obj;
        }, {})
    ));
})();

const style_table = {
    height: 500,
    width: 500
};

const style_data_conditional = [
    { width: 100 }
];

let props = {
    setProps,
    id: 'table',
    data: data,
    columns,
    style_data_conditional,
    style_table
};

let props2 = {
    setProps,
    id: 'table',
    data: data2,
    columns: columns2,
    style_data_conditional,
    style_table
};

storiesOf('DashTable/Border (available space not filled)', module)
    .add('with no frozen rows and no frozen columns', () => (<DashTable
        {...props}
    />))
    .add('with frozen rows and no frozen columns', () => (<DashTable
        {...props}
        n_fixed_rows={1}
    />))
    .add('with no frozen rows and frozen columns', () => (<DashTable
        {...props}
        n_fixed_columns={1}
    />))
    .add('with frozen rows and frozen columns', () => (<DashTable
        {...props}
        n_fixed_columns={1}
        n_fixed_rows={1}
    />));

storiesOf('DashTable/Border (available space filled)', module)
    .add('with no frozen rows and no frozen columns', () => (<DashTable
        {...props2}
    />))
    .add('with frozen rows and no frozen columns', () => (<DashTable
        {...props2}
        n_fixed_rows={1}
    />))
    .add('with no frozen rows and frozen columns', () => (<DashTable
        {...props2}
        n_fixed_columns={1}
    />))
    .add('with frozen rows and frozen columns', () => (<DashTable
        {...props2}
        n_fixed_columns={1}
        n_fixed_rows={1}
    />));