import * as R from 'ramda';
import React from 'react';
import { storiesOf } from '@storybook/react';
import DataTable from 'dash-table/dash/DataTable';
import { ColumnType } from 'dash-table/components/Table/props';

const setProps = () => { };

const date = ['2015-01-01', '2015-10-24', '2016-05-10'];
const region = ['Montreal', 'Vermont', 'New York City'];
const temperature = [1, -20, 3.512];
const humidity = [10, 20, 30];
const pressure = [2, 10924, 3912];

const data: any[] = [];
for (let i = 0; i < 6; ++i) {
    data.push({
        Date: date[i % date.length],
        Region: region[i % region.length],
        Temperature: temperature[i % temperature.length],
        Humidity: humidity[i % humidity.length],
        Pressure: pressure[i % pressure.length]
    });
}

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
    />))
    .add('row padding', () => (<DataTable
        id='styling-2'
        data={data}
        columns={R.map(
            i => ({ name: i, id: i }),
            R.keysIn(data[0]))
        }
        style_data_conditional={[{
            padding_bottom: 5,
            padding_top: 5
        }]}
    />))
    .add('dark theme with cells', () => (<DataTable
        id='styling-6'
        data={data}
        columns={R.map(
            i => ({ name: i, id: i }),
            R.keysIn(data[0]))
        }
        content_style='grow'
        style_table={{
            width: '100%'
        }}
        style_data_conditional={[{
            background_color: 'rgb(50, 50, 50)',
            color: 'white',
            font_family: 'arial'
        }, {
            if: { column_id: 'Humidity' },
            font_family: 'monospace',
            padding_left: 20,
            text_align: 'left'
        }, {
            if: { column_id: 'Pressure' },
            font_family: 'monospace',
            padding_left: 20,
            text_align: 'left'
        }, {
            if: { column_id: 'Temperature' },
            font_family: 'monospace',
            padding_left: 20,
            text_align: 'left'
        }]}
    />))
    .add('highlight columns', () => (<DataTable
        id='styling-9'
        data={data}
        columns={R.map(
            i => ({ name: i, id: i }),
            R.keysIn(data[0]))
        }
        content_style='grow'
        style_table={{
            width: '100%'
        }}
        style_data_conditional={[{
            color: 'rgb(60, 60, 60)',
            padding_left: 20,
            'text-align': 'left',
            width: '20%'
        }, {
            if: { column_id: 'Temperature' },
            background_color: 'yellow'
        }]}
    />))
    .add('highlight cells', () => (<DataTable
        id='styling-10'
        data={data}
        columns={R.map(
            i => ({ name: i, id: i }),
            R.keysIn(data[0]))
        }
        content_style='grow'
        style_table={{
            width: '100%'
        }}
        style_data_conditional={[{
            if: { column_id: 'Region', filter: '{Region} eq Montreal' },
            background_color: 'yellow'
        }, {
            if: { column_id: 'Humidity', filter: '{Humidity} eq 20' },
            background_color: 'yellow'
        }]}
    />))
    .add('single selected cells on dark themes', () => (<DataTable
        id='styling-11'
        data={data}
        selected_cells={[{row: 1, column: 1, column_id: 'Region'}]}
        active_cell={{row: 1, column: 1}}
        columns={R.map(
            i => ({ name: i, id: i }),
            R.keysIn(data[0]))
        }
        content_style='grow'
        style_table={{
            width: '100%'
        }}
        style_data_conditional={[{
            background_color: 'rgb(50, 50, 50)',
            color: 'white',
            font_family: 'arial'
        }]}
    />))
    .add('multiple selected cells on dark themes', () => (<DataTable
        id='styling-12'
        data={data}
        selected_cells={[{row: 1, column: 1, column_id: 'Region'}, {row: 1, column: 2, column_id: 'Temperature'}, {row: 2, column: 1, column_id: 'Region'}, {row: 2, column: 2, column_id: 'Temperature'}]}
        active_cell={{row: 1, column: 1}}
        columns={R.map(
            i => ({ name: i, id: i }),
            R.keysIn(data[0]))
        }
        content_style='grow'
        style_table={{
            width: '100%'
        }}
        style_data_conditional={[{
            background_color: 'rgb(50, 50, 50)',
            color: 'white',
            font_family: 'arial'
        }]}
    />));