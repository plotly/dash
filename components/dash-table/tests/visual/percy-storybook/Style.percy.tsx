import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';
import DataTable from 'dash-table/dash/DataTable';
import {ColumnType} from 'dash-table/components/Table/props';
import {generateMockData} from '../../../demo/data';

const setProps = () => {};

const date = ['2015-01-01', '2015-10-24', '2016-05-10'];
const region = ['Montreal', 'Vermont', 'New York City'];
const temperature = [1, -20, 3.512];
const humidity = [10, 20, 30];
const pressure = [2, 10924, 3912];
const mock = generateMockData(50);
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

const DEFAULT_TABLE = {
    data: [
        {a: 1, b: 2, c: '3', d: '4'},
        {a: 11, b: 22, c: '33', d: '44'},
        {a: 111, b: 222, c: '333', d: '444'}
    ],
    columns: [
        {id: 'a', name: 'A', type: ColumnType.Any},
        {id: 'b', name: 'B', type: ColumnType.Text},
        {id: 'c', name: 'C', type: ColumnType.Numeric},
        {id: 'd', name: 'D'}
    ]
};

storiesOf('DashTable/Style type condition', module).add('all variants', () => (
    <div>
        <div>with 1 column</div>
        <DataTable
            setProps={setProps}
            id='table'
            data={[
                {a: 1, b: 2, c: '3', d: '4', e: 5, f: 6, g: 7, h: 8},
                {a: 11, b: 22, c: '33', d: '44', e: 55, f: 66, g: 77, h: 88},
                {
                    a: 111,
                    b: 222,
                    c: '333',
                    d: '444',
                    e: 555,
                    f: 666,
                    g: 777,
                    h: 888
                }
            ]}
            columns={[
                {id: 'a', name: 'A', type: ColumnType.Any},
                {id: 'b', name: 'B', type: ColumnType.Any},
                {id: 'c', name: 'C', type: ColumnType.Text},
                {id: 'd', name: 'D', type: ColumnType.Text},
                {id: 'e', name: 'E', type: ColumnType.Numeric},
                {id: 'f', name: 'F', type: ColumnType.Numeric},
                {id: 'g', name: 'G'},
                {id: 'h', name: 'H'}
            ]}
            style_data_conditional={[
                {
                    if: {column_type: ColumnType.Any, row_index: 'even'},
                    background_color: 'blue',
                    color: 'white'
                },
                {
                    if: {column_type: ColumnType.Text, row_index: 'even'},
                    background_color: 'red',
                    color: 'white'
                },
                {
                    if: {column_type: ColumnType.Numeric, row_index: 'even'},
                    background_color: 'green',
                    color: 'white'
                },
                {if: {column_type: ColumnType.Any}, background_color: 'blue'},
                {if: {column_type: ColumnType.Text}, background_color: 'red'},
                {
                    if: {column_type: ColumnType.Numeric},
                    background_color: 'green'
                }
            ]}
        />
        <div>row padding</div>
        <DataTable
            id='styling-2'
            data={data}
            columns={R.map(i => ({name: i, id: i}), R.keysIn(data[0]))}
            style_data_conditional={[
                {
                    padding_bottom: 5,
                    padding_top: 5
                }
            ]}
        />
        <div>dark theme with cells</div>
        <DataTable
            id='styling-6'
            data={data}
            columns={R.map(i => ({name: i, id: i}), R.keysIn(data[0]))}
            style_table={{
                width: '100%'
            }}
            style_data_conditional={[
                {
                    background_color: 'rgb(50, 50, 50)',
                    color: 'white',
                    font_family: 'arial'
                },
                {
                    if: {column_id: 'Humidity'},
                    font_family: 'monospace',
                    padding_left: 20,
                    text_align: 'left'
                },
                {
                    if: {column_id: 'Pressure'},
                    font_family: 'monospace',
                    padding_left: 20,
                    text_align: 'left'
                },
                {
                    if: {column_id: 'Temperature'},
                    font_family: 'monospace',
                    padding_left: 20,
                    text_align: 'left'
                }
            ]}
        />
        <div>highlight columns</div>
        <DataTable
            id='styling-9'
            data={data}
            columns={R.map(i => ({name: i, id: i}), R.keysIn(data[0]))}
            style_table={{
                width: '100%'
            }}
            style_data_conditional={[
                {
                    color: 'rgb(60, 60, 60)',
                    padding_left: 20,
                    'text-align': 'left',
                    width: '20%'
                },
                {
                    if: {column_id: 'Temperature'},
                    background_color: 'yellow'
                }
            ]}
        />
        <div>highlight cells</div>
        <DataTable
            id='styling-10'
            data={data}
            columns={R.map(i => ({name: i, id: i}), R.keysIn(data[0]))}
            style_table={{
                width: '100%'
            }}
            style_data_conditional={[
                {
                    if: {
                        column_id: 'Region',
                        filter_query: '{Region} eq Montreal'
                    },
                    background_color: 'yellow'
                },
                {
                    if: {
                        column_id: 'Humidity',
                        filter_query: '{Humidity} eq 20'
                    },
                    background_color: 'yellow'
                }
            ]}
        />
        <div>single selected cells on dark themes</div>
        <DataTable
            id='styling-11'
            data={data}
            selected_cells={[{row: 1, column: 1, column_id: 'Region'}]}
            active_cell={{row: 1, column: 1}}
            columns={R.map(i => ({name: i, id: i}), R.keysIn(data[0]))}
            content_style='grow'
            style_table={{
                width: '100%'
            }}
            style_data_conditional={[
                {
                    background_color: 'rgb(50, 50, 50)',
                    color: 'white',
                    font_family: 'arial'
                }
            ]}
        />
        <div>multiple selected cells on dark themes</div>
        <DataTable
            id='styling-12'
            data={data}
            selected_cells={[
                {row: 1, column: 1, column_id: 'Region'},
                {row: 1, column: 2, column_id: 'Temperature'},
                {row: 2, column: 1, column_id: 'Region'},
                {row: 2, column: 2, column_id: 'Temperature'}
            ]}
            active_cell={{row: 1, column: 1}}
            columns={R.map(i => ({name: i, id: i}), R.keysIn(data[0]))}
            content_style='grow'
            style_table={{
                width: '100%'
            }}
            style_data_conditional={[
                {
                    background_color: 'rgb(50, 50, 50)',
                    color: 'white',
                    font_family: 'arial'
                }
            ]}
        />
        <div>yellow if table is editable</div>
        <DataTable
            id='styling-13'
            data={[
                {a: 1, b: 2, c: '3', d: '4'},
                {a: 11, b: 22, c: '33', d: '44'},
                {a: 111, b: 222, c: '333', d: '444'}
            ]}
            columns={[
                {id: 'a', name: 'A', type: ColumnType.Any},
                {id: 'b', name: 'B', type: ColumnType.Text},
                {id: 'c', name: 'C', type: ColumnType.Numeric},
                {id: 'd', name: 'D'}
            ]}
            editable={true}
            row_deletable={true}
            row_selectable={true}
            style_table={{
                width: '100%'
            }}
            style_data_conditional={[
                {
                    if: {column_editable: true},
                    background_color: 'yellow'
                }
            ]}
        />
        <div>green if table is not editable</div>
        <DataTable
            id='styling-14'
            data={[
                {a: 1, b: 2, c: '3', d: '4'},
                {a: 11, b: 22, c: '33', d: '44'},
                {a: 111, b: 222, c: '333', d: '444'}
            ]}
            style_table={{
                width: '100%'
            }}
            row_deletable={true}
            row_selectable={true}
            columns={[
                {id: 'a', name: 'A', type: ColumnType.Any},
                {id: 'b', name: 'B', type: ColumnType.Text},
                {id: 'c', name: 'C', type: ColumnType.Numeric},
                {id: 'd', name: 'D'}
            ]}
            style_data_conditional={[
                {
                    if: {column_editable: false},
                    background_color: 'green'
                }
            ]}
        />
        <div>first column is editable and blue</div>
        <DataTable
            id='styling-15'
            data={[
                {a: 1, b: 2, c: '3', d: '4'},
                {a: 11, b: 22, c: '33', d: '44'},
                {a: 111, b: 222, c: '333', d: '444'}
            ]}
            style_table={{
                width: '100%'
            }}
            row_deletable={true}
            row_selectable={true}
            columns={[
                {id: 'a', name: 'A', type: ColumnType.Any, editable: true},
                {id: 'b', name: 'B', type: ColumnType.Text},
                {id: 'c', name: 'C', type: ColumnType.Numeric},
                {id: 'd', name: 'D'}
            ]}
            style_data_conditional={[
                {
                    if: {column_editable: true},
                    background_color: 'blue'
                }
            ]}
        />
        <div>first column is editable and not blue</div>
        <DataTable
            id='styling-16'
            data={[
                {a: 1, b: 2, c: '3', d: '4'},
                {a: 11, b: 22, c: '33', d: '44'},
                {a: 111, b: 222, c: '333', d: '444'}
            ]}
            style_table={{
                width: '100%'
            }}
            row_deletable={true}
            row_selectable={true}
            columns={[
                {id: 'a', name: 'A', type: ColumnType.Any, editable: true},
                {id: 'b', name: 'B', type: ColumnType.Text},
                {id: 'c', name: 'C', type: ColumnType.Numeric},
                {id: 'd', name: 'D'}
            ]}
            style_data_conditional={[
                {
                    if: {column_editable: false},
                    background_color: 'DeepSkyBlue'
                }
            ]}
        />
        <div>style header and column based on edibility</div>
        <DataTable
            id='styling-17'
            data={[
                {a: 1, b: 2, c: '3', d: '4'},
                {a: 11, b: 22, c: '33', d: '44'},
                {a: 111, b: 222, c: '333', d: '444'}
            ]}
            row_deletable={true}
            row_selectable={true}
            style_table={{
                width: '100%'
            }}
            columns={[
                {id: 'a', name: 'A', type: ColumnType.Any, editable: true},
                {id: 'b', name: 'B', type: ColumnType.Text},
                {id: 'c', name: 'C', type: ColumnType.Numeric, editable: true},
                {id: 'd', name: 'D'}
            ]}
            style_data_conditional={[
                {
                    if: {column_editable: true},
                    background_color: 'Violet'
                }
            ]}
            style_header_conditional={[
                {
                    if: {column_editable: false},
                    background_color: 'Lavender'
                }
            ]}
        />
        <div>header, filter, column colors depend on editbility</div>
        <DataTable
            id='styling-18'
            data={[
                {a: 1, b: 2, c: '3', d: '4'},
                {a: 11, b: 22, c: '33', d: '44'},
                {a: 111, b: 222, c: '333', d: '444'}
            ]}
            style_table={{
                width: '100%'
            }}
            row_deletable={true}
            row_selectable={true}
            filtering={true}
            columns={[
                {id: 'a', name: 'A', type: ColumnType.Any, editable: true},
                {id: 'b', name: 'B', type: ColumnType.Text},
                {id: 'c', name: 'C', type: ColumnType.Numeric},
                {id: 'd', name: 'D'}
            ]}
            style_data_conditional={[
                {
                    if: {column_editable: true},
                    background_color: 'PaleVioletRed'
                },
                {
                    if: {column_editable: false},
                    background_color: 'DarkTurquoise'
                }
            ]}
            style_header_conditional={[
                {
                    if: {column_editable: true},
                    background_color: 'MediumPurple'
                },
                {
                    if: {column_editable: false},
                    background_color: 'DeepSkyBlue'
                }
            ]}
            style_filter_conditional={[
                {
                    if: {column_editable: true},
                    background_color: 'Violet'
                },
                {
                    if: {column_editable: false},
                    background_color: 'Aquamarine'
                }
            ]}
        />
        <div>column wins over table edibility</div>
        <DataTable
            id='styling-19'
            data={[
                {a: 1, b: 2, c: '3', d: '4'},
                {a: 11, b: 22, c: '33', d: '44'},
                {a: 111, b: 222, c: '333', d: '444'}
            ]}
            style_table={{
                width: '100%'
            }}
            editable={true}
            row_deletable={true}
            row_selectable={true}
            filtering={true}
            columns={[
                {id: 'a', name: 'A', type: ColumnType.Any, editable: false},
                {id: 'b', name: 'B', type: ColumnType.Text},
                {id: 'c', name: 'C', type: ColumnType.Numeric},
                {id: 'd', name: 'D'}
            ]}
            style_data_conditional={[
                {
                    if: {column_editable: false},
                    background_color: 'MediumPurple'
                }
            ]}
            style_header_conditional={[
                {
                    if: {column_editable: false},
                    background_color: 'MediumPurple'
                }
            ]}
            style_filter_conditional={[
                {
                    if: {column_editable: false},
                    background_color: 'MediumPurple'
                }
            ]}
        />
        <div>paging</div>
        <DataTable
            id='styling-20'
            data={mock.data}
            columns={mock.columns.map((col: any) =>
                R.mergeRight(col, {
                    name: col.name,
                    deletable: true
                })
            )}
            style_table={{
                width: '100%'
            }}
            row_deletable={true}
            row_selectable={true}
            pagination_mode={'fe'}
            style_data_conditional={[
                {
                    if: {column_editable: true},
                    background_color: 'MediumPurple'
                }
            ]}
            page_current={0}
            page_size={10}
        />
        <div>large current page</div>
        <DataTable
            id='paging-large-current-page'
            data={mock.data.slice(0, 10)}
            columns={mock.columns.map((col: any) =>
                R.mergeRight(col, {
                    name: col.name,
                    deletable: true
                })
            )}
            style_table={{
                width: '100%'
            }}
            row_deletable={true}
            row_selectable={true}
            pagination_mode={'fe'}
            style_data_conditional={[
                {
                    if: {column_editable: true},
                    background_color: 'MediumPurple'
                }
            ]}
            page_action='custom'
            page_count={999999}
            page_current={987654}
            page_size={10}
        />
        <div>large current page and unknown page count</div>
        <DataTable
            id='paging-large-current-page'
            data={mock.data.slice(0, 10)}
            columns={mock.columns.map((col: any) =>
                R.mergeRight(col, {
                    name: col.name,
                    deletable: true
                })
            )}
            style_table={{
                width: '100%'
            }}
            row_deletable={true}
            row_selectable={true}
            pagination_mode={'fe'}
            style_data_conditional={[
                {
                    if: {column_editable: true},
                    background_color: 'MediumPurple'
                }
            ]}
            page_action='custom'
            page_current={987654}
            page_size={10}
        />
        <div>data column_id array</div>
        <DataTable
            {...DEFAULT_TABLE}
            id='data-column-id-array'
            style_data_conditional={[
                {
                    if: {
                        column_id: ['a', 'b', 'd']
                    },
                    backgroundColor: 'MediumPurple'
                }
            ]}
        />
        <div>data row_index array</div>
        <DataTable
            {...DEFAULT_TABLE}
            id='data-column-id-array'
            style_data_conditional={[
                {
                    if: {
                        row_index: [0, 2]
                    },
                    backgroundColor: 'MediumPurple'
                }
            ]}
        />
        <div>header header_index array</div>
        <DataTable
            setProps={setProps}
            id='table'
            {...DEFAULT_TABLE}
            columns={DEFAULT_TABLE.columns.map(c => ({
                ...c,
                name: [c.name, c.name, c.name]
            }))}
            style_header_conditional={[
                {
                    if: {header_index: [0, 2]},
                    background_color: 'blue',
                    color: 'white'
                }
            ]}
        />
        <div>cell column_id array</div>
        <DataTable
            {...DEFAULT_TABLE}
            id='data-column-id-array'
            style_cell_conditional={[
                {
                    if: {
                        column_id: ['a', 'b', 'd']
                    },
                    backgroundColor: 'MediumPurple'
                }
            ]}
        />
        <div>filter column_id array</div>
        <DataTable
            {...DEFAULT_TABLE}
            id='data-column-id-array'
            filter_action='native'
            style_filter_conditional={[
                {
                    if: {
                        column_id: ['a', 'b', 'd']
                    },
                    backgroundColor: 'MediumPurple'
                }
            ]}
        />
        <div>header column_id array</div>
        <DataTable
            {...DEFAULT_TABLE}
            id='data-column-id-array'
            style_header_conditional={[
                {
                    if: {
                        column_id: ['a', 'b', 'd']
                    },
                    backgroundColor: 'MediumPurple'
                }
            ]}
        />
        <div>active styling</div>
        <DataTable
            {...DEFAULT_TABLE}
            id='active-styling'
            style_data_conditional={[
                {
                    if: {
                        state: 'active'
                    },
                    backgroundColor: 'lightblue',
                    border: '1px solid blue'
                }
            ]}
            active_cell={{row: 1, column: 1}}
        />
        <div>selected styling (applied to active)</div>
        <DataTable
            {...DEFAULT_TABLE}
            id='data-column-id-array'
            style_data_conditional={[
                {
                    if: {
                        state: 'selected'
                    },
                    backgroundColor: 'lightblue',
                    border: '1px solid blue'
                }
            ]}
            selected_cells={[
                {row: 1, column: 1, column_id: 'b'},
                {row: 1, column: 2, column_id: 'c'},
                {row: 2, column: 1, column_id: 'b'},
                {row: 2, column: 2, column_id: 'c'}
            ]}
            active_cell={{row: 1, column: 1}}
        />
        <div>active styling partially overrides selected</div>
        <DataTable
            {...DEFAULT_TABLE}
            id='data-column-id-array'
            style_data_conditional={[
                {
                    if: {
                        state: 'selected'
                    },
                    backgroundColor: 'lightblue',
                    border: '1px solid blue'
                },
                {
                    if: {
                        state: 'active'
                    },
                    color: 'white',
                    border: '2px solid white'
                }
            ]}
            selected_cells={[
                {row: 1, column: 1, column_id: 'b'},
                {row: 1, column: 2, column_id: 'c'},
                {row: 2, column: 1, column_id: 'b'},
                {row: 2, column: 2, column_id: 'c'}
            ]}
            active_cell={{row: 1, column: 1}}
        />
        <div>active styling overrides selected</div>
        <DataTable
            {...DEFAULT_TABLE}
            id='data-column-id-array'
            style_data_conditional={[
                {
                    if: {
                        state: 'selected'
                    },
                    backgroundColor: 'lightblue',
                    border: '1px solid blue'
                },
                {
                    if: {
                        state: 'active'
                    },
                    backgroundColor: 'black',
                    color: 'white',
                    border: '1px solid white'
                }
            ]}
            selected_cells={[
                {row: 1, column: 1, column_id: 'b'},
                {row: 1, column: 2, column_id: 'c'},
                {row: 2, column: 1, column_id: 'b'},
                {row: 2, column: 2, column_id: 'c'}
            ]}
            active_cell={{row: 1, column: 1}}
        />
        <div>unselectable cells</div>
        <DataTable
            {...DEFAULT_TABLE}
            id='unselectable-cells'
            cell_selectable={false}
            selected_cells={[
                {row: 1, column: 1, column_id: 'b'},
                {row: 1, column: 2, column_id: 'c'},
                {row: 2, column: 1, column_id: 'b'},
                {row: 2, column: 2, column_id: 'c'}
            ]}
            active_cell={{row: 1, column: 1}}
        />
    </div>
));
