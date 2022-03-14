import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';
import DataTable from 'dash-table/dash/DataTable';

const setProps = () => {};

const data = [
    {
        a: 'A',
        b: 'BBBBB',
        c: 'CCCCCCCCCC',
        d: 'DDDDDDDDDDDDDDD',
        e: 'EEEEEEEEEEEEEEEEEEEE',
        f: 'FFFFFFFFFFFFFFFFFFFFFFFFF'
    }
];
const cols = ['a', 'b', 'c', 'd', 'e', 'f'].map(i => ({
    name: `Column ${i.toUpperCase()}`,
    id: i,
    selectable: true
}));
const colsEditable = cols.map(col => ({
    editable: true,
    renamable: true,
    deletable: true,
    ...col
}));
const common = {style_table: {width: 'auto', marginBottom: '10px'}};
const allActions = {
    sort_action: 'native',
    column_selectable: 'single',
    editable: true
};

const alignments: [React.ReactNode?] = [];

[{}, {sort_action: 'native'}, allActions].forEach(actionProps => {
    ['left', 'center', 'right'].forEach(alignment => {
        alignments.push(
            <DataTable
                data={data}
                columns={actionProps === allActions ? colsEditable : cols}
                style_header={{textAlign: alignment}}
                {...actionProps}
                {...common}
            />
        );
    });
});

storiesOf('DashTable/Headers', module)
    .add('multi header', () => (
        <DataTable
            setProps={setProps}
            id='multi-header'
            data={R.map(
                i => ({
                    year: i,
                    montreal: i * 10,
                    toronto: i * 100,
                    ottawa: i * -1,
                    vancouver: i * -10,
                    temp: i * -100,
                    humidity: i * 0.1
                }),
                R.range(0, 100)
            )}
            columns={[
                {name: ['Year', ''], id: 'year'},
                {name: ['City', 'Montreal'], id: 'montreal'},
                {name: ['City', 'Toronto'], id: 'toronto'},
                {name: ['City', 'Ottawa'], id: 'ottawa'},
                {name: ['City', 'Vancouver'], id: 'vancouver'},
                {name: ['Climate', 'Temperature'], id: 'temp'},
                {name: ['Climate', 'Humidity'], id: 'humidity'}
            ]}
        />
    ))
    .add('alignment and actions', () => (
        <div style={{width: '100px'}}>{alignments}</div>
    ));
