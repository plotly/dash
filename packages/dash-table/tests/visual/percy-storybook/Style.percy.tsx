import React from 'react';
import { storiesOf } from '@storybook/react';
import DataTable from 'dash-table/DataTable';
import fixtures from './fixtures';
import { ColumnType } from 'dash-table/components/Table/props';

const setProps = () => { };

// Legacy: Tests previously run in Python
const fixtureStories = storiesOf('DashTable/Fixtures', module);
fixtures.forEach(fixture => fixtureStories.add(fixture.name, () => (<DataTable {...Object.assign(fixture.props)} />)));

storiesOf('DashTable/Style type condition', module)
    .add('with 1 column', () => (<DataTable
        setProps={setProps}
        id='table'
        data={[
            { a: 1, b: 2, c: '3', d: '4', e: 5, f: 6, g: 7, h: 8 },
            { a: 11, b: 22, c: '33', d: '44', e: 55, f: 66, g: 77, h: 88 },
            { a: 111, b: 222, c: '333', d: '444', e: 555, f: 666, g: 777, h: 888 }
        ]}
        columns={[
            { id: 'a', name: 'A', type: ColumnType.Any },
            { id: 'b', name: 'B', type: ColumnType.Any },
            { id: 'c', name: 'C', type: ColumnType.Text },
            { id: 'd', name: 'D', type: ColumnType.Text },
            { id: 'e', name: 'E', type: ColumnType.Numeric },
            { id: 'f', name: 'F', type: ColumnType.Numeric },
            { id: 'g', name: 'G' },
            { id: 'h', name: 'H' }
        ]}
        style_data_conditional={[
            { if: { column_type: ColumnType.Any, row_index: 'even' }, background_color: 'blue', color: 'white' },
            { if: { column_type: ColumnType.Text, row_index: 'even' }, background_color: 'red', color: 'white' },
            { if: { column_type: ColumnType.Numeric, row_index: 'even' }, background_color: 'green', color: 'white' },
            { if: { column_type: ColumnType.Any }, background_color: 'blue' },
            { if: { column_type: ColumnType.Text }, background_color: 'red' },
            { if: { column_type: ColumnType.Numeric }, background_color: 'green' }
        ]}
    />));