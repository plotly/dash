import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';
import DataTable from 'dash-table/dash/DataTable';

const setProps = () => {};
const columns: {name: string[]; id: string; presentation?: string}[] = [
    {name: ['String'], id: 'string'},
    {name: ['Number'], id: 'number'},
    {name: ['Date'], id: 'date'},
    {name: ['Boolean'], id: 'boolean'},
    {name: ['Any'], id: 'any'}
];

const columns_dd = columns.map(i => ({...i, presentation: 'dropdown'}));

storiesOf('DashTable/Types', module).add('types input & dropdown', () => (
    <div>
        <DataTable
            setProps={setProps}
            id='types input'
            data={[
                {
                    string: 'Montreal',
                    number: 1,
                    date: '2015-01-01',
                    boolean: true,
                    any: 'Montreal'
                },
                {
                    string: 'Vermont',
                    number: 2,
                    date: '2015-10-24',
                    boolean: false,
                    any: 1
                },
                {
                    string: 'New York City',
                    number: 3,
                    date: '2016-05-10',
                    boolean: true,
                    any: '2015-01-01'
                },
                {
                    string: 'Boston',
                    number: 4,
                    date: '2017-11-11',
                    boolean: false,
                    any: true
                }
            ]}
            columns={columns}
        />
        <DataTable
            setProps={setProps}
            id='types dropdown'
            data={[
                {
                    string: 'Montreal',
                    number: 1,
                    date: '2015-01-01',
                    boolean: true,
                    any: 'Montreal'
                },
                {
                    string: 'Vermont',
                    number: 2,
                    date: '2015-10-24',
                    boolean: false,
                    any: 1
                },
                {
                    string: 'New York City',
                    number: 3,
                    date: '2016-05-10',
                    boolean: true,
                    any: '2015-01-01'
                },
                {
                    string: 'Boston',
                    number: 4,
                    date: '2017-11-11',
                    boolean: false,
                    any: true
                }
            ]}
            columns={columns_dd}
            editable={false}
            dropdown={{
                string: {
                    options: R.map(
                        i => ({label: `label: ${i}`, value: i}),
                        ['Montreal', 'Vermont', 'New York City', 'Boston']
                    )
                },
                number: {
                    options: R.map(
                        i => ({label: `label: ${i}`, value: i}),
                        [1, 2, 3, 4]
                    )
                },
                date: {
                    options: R.map(
                        i => ({label: `label: ${i}`, value: i}),
                        ['2015-01-01', '2015-10-24', '2016-05-10', '2017-11-11']
                    )
                },
                boolean: {
                    options: R.map(
                        i => ({label: `label: ${i}`, value: i}),
                        [true, false]
                    )
                },
                any: {
                    options: R.map(
                        i => ({label: `label: ${i}`, value: i}),
                        ['Montreal', 1, '2015-01-01', true]
                    )
                }
            }}
        />
    </div>
));
