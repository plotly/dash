import * as R from 'ramda';
import React from 'react';
import { storiesOf } from '@storybook/react';
import random from 'core/math/random';
import DashTable from 'dash-table/Table';

const setProps = () => { };

const columns = ['a', 'b', 'c']
    .map(id => ({ id: id, name: id.toUpperCase(), width: '100px' }));

const dataframe = (() => {
    const r = random(1);

    return R.range(0, 5).map(() => (
        ['a', 'b', 'c'].reduce((obj: any, key) => {
            obj[key] = Math.floor(r() * 1000);
            return obj;
        }, {})
    ));
})();

const columns2 = ['a', 'b', 'c', 'd', 'e', 'f']
    .map(id => ({ id: id, name: id.toUpperCase(), width: '100px' }));

const dataframe2 = (() => {
    const r = random(1);

    return R.range(0, 50).map(() => (
        ['a', 'b', 'c', 'd', 'e', 'f'].reduce((obj: any, key) => {
            obj[key] = Math.floor(r() * 1000);
            return obj;
        }, {})
    ));
})();

let props = {
    setProps,
    id: 'table',
    dataframe,
    columns,
    table_style: [{
        selector: '.dash-spreadsheet', rule: 'width: 500px; height: 500px;'
    }]
};

let props2 = {
    setProps,
    id: 'table',
    dataframe: dataframe2,
    columns: columns2,
    table_style: [{
        selector: '.dash-spreadsheet', rule: 'width: 500px; height: 500px;'
    }]
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