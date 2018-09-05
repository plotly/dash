import * as R from 'ramda';
import React from 'react';
import { storiesOf } from '@storybook/react';
import random from 'core/math/random';
import DashTable from 'dash-table/Table';
import fixtures from './fixtures';

const setProps = () => { };

// Legacy: Tests previously run in Python
const fixtureStories = storiesOf('DashTable/Fixtures');
fixtures.forEach(fixture => fixtureStories.add(fixture.name, () => (<DashTable {...Object.assign(fixture.props)} />)));

storiesOf('DashTable/Without Data', module)
    .add('with 1 column', () => (<DashTable
        setProps={setProps}
        id='table'
        dataframe={[]}
        columns={[{ id: 'a', name: 'A' }]}
        sorting={false}
        editable={false}
        row_deletable={false}
        row_selectable={false}
    />));

storiesOf('DashTable/With Data', module)
    .add('with 3 columns and 3 rows, not actionable', () => (<DashTable
        setProps={setProps}
        id='table'
        dataframe={[
            { a: 1, b: 2, c: 3 },
            { a: 11, b: 12, c: 13 },
            { a: 21, b: 22, c: 23 }
        ]}
        columns={[
            { id: 'a', name: 'A', width: '100px' },
            { id: 'b', name: 'B', width: '50px' },
            { id: 'c', name: 'C', width: '200px' }
        ]}
        editable={false}
        sorting={false}
        row_deletable={false}
        row_selectable={false}
    />));

const columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    .map(id => ({ id: id, name: id.toUpperCase(), width: '100px' }));

const idMap: { [key: string]: number } = {
    a: 0,
    b: 0,
    c: 1,
    d: 1,
    e: 2,
    f: 2,
    g: 2,
    h: 3,
    i: 3,
    j: 3
};

const mergedColumns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    .map(id => ({ id: id, name: [idMap[id], id.toUpperCase()], width: '100px' }));

const dataframe = (() => {
    const r = random(0);

    return R.range(0, 100).map(() => (
        ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'].reduce((obj: any, key) => {
            obj[key] = r() % 1000;
            return obj;
        }, {})
    ));
})();

storiesOf('DashTable/Fixed Rows & Columns', module)
    .add('with 1 fixed row, 2 fixed columns, default height/width', () => (<DashTable
        setProps={setProps}
        id='table'
        dataframe={dataframe}
        columns={columns}
        n_fixed_columns={2}
        n_fixed_rows={1}
        row_deletable={true}
        row_selectable={true}
    />))
    .add('with 1 fixed row, default height', () => (<DashTable
        setProps={setProps}
        id='table'
        dataframe={dataframe}
        columns={columns}
        n_fixed_rows={1}
        row_deletable={true}
        row_selectable={true}
    />))
    .add('with 2 fixed columns, default width', () => (<DashTable
        setProps={setProps}
        id='table'
        dataframe={dataframe}
        columns={columns}
        n_fixed_columns={2}
        row_deletable={true}
        row_selectable={true}
    />))
    .add('with 2 fixed rows, 4 fixed columns and merged cells', () => (<DashTable
        setProps={setProps}
        id='table'
        dataframe={dataframe}
        columns={mergedColumns}
        merge_duplicate_headers={true}
        n_fixed_columns={4}
        n_fixed_rows={2}
    />))
    .add('with 2 fixed rows, 3 fixed columns, hidden columns and merged cells', () => {
        const testColumns = JSON.parse(JSON.stringify(mergedColumns));
        testColumns[2].hidden = true;

        return (<DashTable
            setProps={setProps}
            id='table'
            dataframe={dataframe}
            columns={mergedColumns}
            merge_duplicate_headers={true}
            n_fixed_columns={3}
            n_fixed_rows={2}
        />);
    });