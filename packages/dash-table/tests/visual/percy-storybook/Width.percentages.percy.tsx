import * as R from 'ramda';
import React from 'react';
import { storiesOf } from '@storybook/react';
import random from 'core/math/random';
import DashTable from 'dash-table/Table';
const setProps = () => { };

const columns = ['a', 'b', 'c'];

const data = (() => {
    const r = random(1);

    return R.range(0, 5).map(() => (
        ['a', 'b', 'c'].reduce((obj: any, key) => {
            obj[key] = Math.floor(r() * 1000);
            return obj;
        }, {})
    ));
})();

const baseProps = {
    setProps,
    id: 'table',
    data
};

const props = Object.assign({}, baseProps, {
    content_style: 'grow',
    columns: columns.map((id => ({ id: id, name: id.toUpperCase(), width: '33%' }))),
    css: [{
        selector: '.dash-spreadsheet',
        rule: 'width: 1000px; max-width: 1000px; height: 1000px;'
    }, {
        selector: '.dash-fixed-column',
        rule: 'width: 33%;'
    }]
});

storiesOf('DashTable/Width percentages', module)
    .add('without frozen columns or rows', () => (<DashTable
        { ...props }
        />))
    .add('with frozen rows', () => (<DashTable
        { ...props }
        n_fixed_rows = { 1}
        />))
    .add('with frozen columns', () => (<DashTable
        { ...props }
        n_fixed_columns = { 1}
    />))
    .add('with frozen rows and frozen columns', () => (<DashTable
        { ...props }
        n_fixed_columns = { 1}
        n_fixed_rows = { 1}
    />));