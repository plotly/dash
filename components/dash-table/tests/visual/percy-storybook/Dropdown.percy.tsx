import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';

import DataTable from 'dash-table/dash/DataTable';

const setProps = () => {};

const data = [
    {climate: 'Sunny', temperature: 13, city: 'NYC'},
    {climate: 'Snowy', temperature: 43, city: 'Montreal'},
    {climate: 'Sunny', temperature: 50, city: 'Miami'},
    {climate: 'Rainy', temperature: 30, city: 'NYC'}
];

const data2 = [
    {City: 'NYC', Neighborhood: 'Brooklyn', 'Temperature (F)': 70},
    {City: 'Montreal', Neighborhood: 'Mile End', 'Temperature (F)': 60},
    {City: 'Los Angeles', Neighborhood: 'Venice', 'Temperature (F)': 90}
];

const columns = R.map(
    i => ({name: i, id: i, presentation: 'dropdown'}),
    ['climate', 'temperature', 'city']
);

const columns2 = R.map(
    i => ({name: i, id: i, presentation: 'dropdown'}),
    ['City', 'Neighborhood', 'Temperature (F)']
);

storiesOf('DashTable/Dropdown', module).add('all variants', () => (
    <div>
        <div>readonly dropdown shows label</div>
        <DataTable
            setProps={setProps}
            data={data}
            columns={columns}
            editable={false}
            dropdown={{
                climate: {
                    options: R.map(
                        i => ({label: `label: ${i}`, value: i}),
                        ['Sunny', 'Snowy', 'Rainy']
                    )
                },
                city: {
                    options: R.map(
                        i => ({label: `label: ${i}`, value: i}),
                        ['NYC', 'Montreal', 'Miami']
                    )
                }
            }}
        />
        <div>editable dropdown shows label</div>
        <DataTable
            setProps={setProps}
            data={data}
            columns={columns}
            editable={true}
            dropdown={{
                climate: {
                    options: R.map(
                        i => ({label: `label: ${i}`, value: i}),
                        ['Sunny', 'Snowy', 'Rainy']
                    )
                },
                city: {
                    options: R.map(
                        i => ({label: `label: ${i}`, value: i}),
                        ['NYC', 'Montreal', 'Miami']
                    )
                }
            }}
        />
        <div>dropdown by column</div>
        <DataTable
            setProps={setProps}
            data={data}
            columns={columns}
            editable={true}
            dropdown={{
                climate: {
                    options: R.map(
                        i => ({label: i, value: i}),
                        ['Sunny', 'Snowy', 'Rainy']
                    )
                },
                city: {
                    options: R.map(
                        i => ({label: i, value: i}),
                        ['NYC', 'Montreal', 'Miami']
                    )
                }
            }}
        />
        <div>dropdown by filtering</div>
        <DataTable
            setProps={setProps}
            data={data2}
            columns={columns2}
            editable={true}
            dropdown_conditional={[
                {
                    if: {
                        column_id: 'Neighborhood',
                        filter_query: '{City} eq "NYC"'
                    },
                    options: R.map(
                        i => ({label: i, value: i}),
                        ['Brooklyn', 'Queens', 'Staten Island']
                    )
                },
                {
                    if: {
                        column_id: 'Neighborhood',
                        filter_query: '{City} eq "Montreal"'
                    },
                    options: R.map(
                        i => ({label: i, value: i}),
                        ['Mile End', 'Plateau', 'Hochelaga']
                    )
                },
                {
                    if: {
                        column_id: 'Neighborhood',
                        filter_query: '{City} eq "Los Angeles"'
                    },
                    options: R.map(
                        i => ({label: i, value: i}),
                        ['Venice', 'Hollywood', 'Los Feliz']
                    )
                }
            ]}
        />
        <div>dropdown by cell (deprecated)</div>
        <DataTable
            setProps={setProps}
            data={data2}
            columns={columns2}
            editable={true}
            dropdown_data={[
                {
                    Neighborhood: {
                        options: R.map(
                            i => ({label: i, value: i}),
                            ['Brooklyn', 'Queens', 'Staten Island']
                        )
                    }
                },
                {
                    Neighborhood: {
                        options: R.map(
                            i => ({label: i, value: i}),
                            ['Mile End', 'Plateau', 'Hochelaga']
                        )
                    }
                },
                {
                    Neighborhood: {
                        options: R.map(
                            i => ({label: i, value: i}),
                            ['Venice', 'Hollywood', 'Los Feliz']
                        )
                    }
                }
            ]}
        />
        <div>dropdown when data are loading (disabled)</div>
        <DataTable
            setProps={setProps}
            data={data2}
            columns={columns2}
            editable={true}
            dropdown_data={[
                {
                    Neighborhood: {
                        options: R.map(
                            i => ({label: i, value: i}),
                            ['Brooklyn', 'Queens', 'Staten Island']
                        )
                    }
                },
                {
                    Neighborhood: {
                        options: R.map(
                            i => ({label: i, value: i}),
                            ['Mile End', 'Plateau', 'Hochelaga']
                        )
                    }
                },
                {
                    Neighborhood: {
                        options: R.map(
                            i => ({label: i, value: i}),
                            ['Venice', 'Hollywood', 'Los Feliz']
                        )
                    }
                }
            ]}
            loading_state={{
                is_loading: true,
                prop_name: 'data',
                component_name: 'table'
            }}
        />
        <div>dropdown when another prop is loading (not disabled)</div>
        <DataTable
            setProps={setProps}
            data={data2}
            columns={columns2}
            editable={true}
            dropdown_data={[
                {
                    Neighborhood: {
                        options: R.map(
                            i => ({label: i, value: i}),
                            ['Brooklyn', 'Queens', 'Staten Island']
                        )
                    }
                },
                {
                    Neighborhood: {
                        options: R.map(
                            i => ({label: i, value: i}),
                            ['Mile End', 'Plateau', 'Hochelaga']
                        )
                    }
                },
                {
                    Neighborhood: {
                        options: R.map(
                            i => ({label: i, value: i}),
                            ['Venice', 'Hollywood', 'Los Feliz']
                        )
                    }
                }
            ]}
            loading_state={{
                is_loading: true,
                prop_name: 'style_cell_conditional',
                component_name: 'table'
            }}
        />
        <div>dropdown when nothing in the table is loading (not disabled)</div>
        <DataTable
            setProps={setProps}
            data={data2}
            columns={columns2}
            editable={true}
            dropdown_data={[
                {
                    Neighborhood: {
                        options: R.map(
                            i => ({label: i, value: i}),
                            ['Brooklyn', 'Queens', 'Staten Island']
                        )
                    }
                },
                {
                    Neighborhood: {
                        options: R.map(
                            i => ({label: i, value: i}),
                            ['Mile End', 'Plateau', 'Hochelaga']
                        )
                    }
                },
                {
                    Neighborhood: {
                        options: R.map(
                            i => ({label: i, value: i}),
                            ['Venice', 'Hollywood', 'Los Feliz']
                        )
                    }
                }
            ]}
            loading_state={{
                is_loading: false,
                prop_name: 'data',
                component_name: 'table'
            }}
        />
    </div>
));
