import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';

import DataTable from 'dash-table/dash/DataTable';

const setProps = () => {};

const data = [
    {City: 'NYC', Neighborhood: 'Brooklyn', 'Temperature (F)': 70},
    {City: 'Montreal', Neighborhood: 'Mile End', 'Temperature (F)': 60},
    {City: 'Los Angeles', Neighborhood: 'Venice', 'Temperature (F)': 90}
];

const columns = R.map(
    i => ({name: i, id: i, presentation: 'dropdown'}),
    ['City', 'Neighborhood', 'Temperature (F)']
);

storiesOf('DashTable/Dropdown', module)
    .add('dropdown when data are loading (disabled)', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={data}
            columns={columns}
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
    ))
    .add('dropdown when another prop is loading (not disabled)', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={data}
            columns={columns}
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
    ))
    .add('dropdown when nothing in the table is loading (not disabled)', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={data}
            columns={columns}
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
    ));
