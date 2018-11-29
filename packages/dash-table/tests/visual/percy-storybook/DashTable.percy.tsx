import * as R from 'ramda';
import React from 'react';
import { storiesOf } from '@storybook/react';
import random from 'core/math/random';
import DataTable from 'dash-table/DataTable';
import fixtures from './fixtures';

const setProps = () => { };

// Legacy: Tests previously run in Python
const fixtureStories = storiesOf('DashTable/Fixtures', module);
fixtures.forEach(fixture => fixtureStories.add(fixture.name, () => (<DataTable {...Object.assign(fixture.props)} />)));

storiesOf('DashTable/Without Data', module)
    .add('with 1 column', () => (<DataTable
        setProps={setProps}
        id='table'
        data={[]}
        columns={[{ id: 'a', name: 'A' }]}
        sorting={false}
        editable={false}
        row_deletable={false}
        row_selectable={false}
    />));

storiesOf('DashTable/With Data', module)
    .add('with 3 columns and 3 rows, not actionable', () => (<DataTable
        setProps={setProps}
        id='table'
        data={[
            { a: 1, b: 2, c: 3 },
            { a: 11, b: 12, c: 13 },
            { a: 21, b: 22, c: 23 }
        ]}
        columns={[
            { id: 'a', name: 'A' },
            { id: 'b', name: 'B' },
            { id: 'c', name: 'C' }
        ]}
        editable={false}
        sorting={false}
        row_deletable={false}
        row_selectable={false}
        style_data_conditional={[
            { if: { column_id: 'a' }, width: '100px' },
            { if: { column_id: 'b' }, width: '50px' },
            { if: { column_id: 'c' }, width: '200px' }
        ]}
    />));

const columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    .map(id => ({ id: id, name: id.toUpperCase() }));

const idMap: { [key: string]: string } = {
    a: 'A',
    b: 'A',
    c: 'B',
    d: 'B',
    e: 'C',
    f: 'C',
    g: 'C',
    h: 'D',
    i: 'D',
    j: 'D'
};

const mergedColumns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    .map(id => ({ id: id, name: [idMap[id], id.toUpperCase()] }));

const data = (() => {
    const r = random(1);

    return R.range(0, 100).map(() => (
        ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'].reduce((obj: any, key) => {
            obj[key] = Math.floor(r() * 1000);
            return obj;
        }, {})
    ));
})();

const style_data_conditional = [
    { width: '100px' }
];

storiesOf('DashTable/Fixed Rows & Columns', module)
    .add('with 1 fixed row, 2 fixed columns', () => (<DataTable
        setProps={setProps}
        id='table'
        data={data}
        columns={columns}
        n_fixed_columns={2}
        n_fixed_rows={1}
        row_deletable={true}
        row_selectable={true}
        style_data_conditional={style_data_conditional}
    />))
    .add('with 1 fixed row', () => (<DataTable
        setProps={setProps}
        id='table'
        data={data}
        columns={columns}
        n_fixed_rows={1}
        row_deletable={true}
        row_selectable={true}
        style_data_conditional={style_data_conditional}
    />))
    .add('with 2 fixed columns', () => (<DataTable
        setProps={setProps}
        id='table'
        data={data}
        columns={columns}
        n_fixed_columns={2}
        row_deletable={true}
        row_selectable={true}
        style_data_conditional={style_data_conditional}
    />))
    .add('with 2 fixed rows, 4 fixed columns and merged cells', () => (<DataTable
        setProps={setProps}
        id='table'
        data={data}
        columns={mergedColumns}
        merge_duplicate_headers={true}
        n_fixed_columns={4}
        n_fixed_rows={2}
        style_data_conditional={style_data_conditional}
    />))
    .add('with 2 fixed rows, 3 fixed columns, hidden columns and merged cells', () => {
        const testColumns = JSON.parse(JSON.stringify(columns));
        testColumns[2].hidden = true;

        return (<DataTable
            setProps={setProps}
            id='table'
            data={data}
            columns={mergedColumns}
            merge_duplicate_headers={true}
            n_fixed_columns={3}
            n_fixed_rows={2}
            style_data_conditional={style_data_conditional}
        />);
    });

const sparseData = (() => {
    const r = random(1);

    return R.range(0, 10).map(index => (
        ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'].reduce((obj: any, key) => {
            obj[key] = index <= 5 ? '' : Math.floor(r() * 1000);
            return obj;
        }, {})
    ));
})();

const hiddenColumns = R.addIndex(R.map)((column, index) =>
    R.mergeAll([
        {},
        column,
        { hidden: index % 2 === 0 }
    ]),
    columns
);

storiesOf('DashTable/Hidden Columns', module)
    .add('hides', () => (<DataTable
        setProps={setProps}
        id='table'
        data={data}
        columns={hiddenColumns}
        style_data_conditional={style_data_conditional}
    />))
    .add('active cell', () => (<DataTable
        setProps={setProps}
        id='table'
        data={data}
        columns={hiddenColumns}
        active_cell={[1, 1]}
        style_data_conditional={style_data_conditional}
    />))
    .add('selected cells', () => (<DataTable
        setProps={setProps}
        id='table'
        data={data}
        columns={hiddenColumns}
        selected_cells={[[1, 1], [1, 2], [2, 1], [2, 2]]}
        style_data_conditional={style_data_conditional}
    />));

storiesOf('DashTable/Sorting', module)
    .add('"a" ascending', () => (<DataTable
        setProps={setProps}
        id='table'
        data={sparseData}
        columns={mergedColumns}
        sorting={true}
        sorting_settings={[{ column_id: 'a', direction: 'asc' }]}
        style_data_conditional={style_data_conditional}
    />))
    .add('"a" descending', () => (<DataTable
        setProps={setProps}
        id='table'
        data={sparseData}
        columns={mergedColumns}
        sorting={true}
        sorting_settings={[{ column_id: 'a', direction: 'desc' }]}
        style_data_conditional={style_data_conditional}
    />))
    .add('"a" ascending -- empty string override', () => (<DataTable
        setProps={setProps}
        id='table'
        data={sparseData}
        columns={mergedColumns}
        sorting={true}
        sorting_settings={[{ column_id: 'a', direction: 'asc' }]}
        sorting_treat_empty_string_as_none={true}
        style_data_conditional={style_data_conditional}
    />))
    .add('"a" descending -- empty string override', () => (<DataTable
        setProps={setProps}
        id='table'
        data={sparseData}
        columns={mergedColumns}
        sorting={true}
        sorting_settings={[{ column_id: 'a', direction: 'desc' }]}
        sorting_treat_empty_string_as_none={true}
        style_data_conditional={style_data_conditional}
    />));
storiesOf('DashTable/Without id', module)
    .add('with 1 fixed row, 2 fixed columns', () => (<DataTable
        setProps={setProps}
        data={data}
        columns={columns}
        n_fixed_columns={2}
        n_fixed_rows={1}
        row_deletable={true}
        row_selectable={true}
        style_data_conditional={style_data_conditional}
    />))
    .add('with 1 fixed row, 2 fixed columns, set height and width', () => (<DataTable
        setProps={setProps}
        data={data}
        columns={columns}
        n_fixed_columns={2}
        n_fixed_rows={1}
        row_deletable={true}
        row_selectable={true}
        style_table={{height: 500, width: 200}}
        style_data_conditional={style_data_conditional}
    />))
    .add('with set height and width and colors', () => (<DataTable
        setProps={setProps}
        data={data}
        columns={columns}
        n_fixed_columns={2}
        n_fixed_rows={1}
        row_deletable={true}
        row_selectable={true}
        style_table={{height: 500, width: 200}}
        style_data_conditional={[{
            if: { column_id: 'a'},
            background_color: 'yellow'
        }]}
    />))
    .add('Two tables with CSS props set', () => (<div>
        <DataTable
            setProps={setProps}
            data={data}
            columns={columns}
            n_fixed_columns={2}
            n_fixed_rows={1}
            row_deletable={true}
            row_selectable={true}
            style_table={{height: 500, width: 400}}
            css={[{
                selector: '.dash-spreadsheet',
                rule: 'border: 4px solid hotpink'
            }]}
        />
        <DataTable
            setProps={setProps}
            data={data}
            columns={columns}
            n_fixed_columns={2}
            n_fixed_rows={1}
            row_deletable={true}
            row_selectable={true}
            style_table={{height: 500, width: 400}}
            css={[{
                selector: '.dash-spreadsheet',
                rule: 'border: 4px solid cyan'
            }]}
        />
    </div>));