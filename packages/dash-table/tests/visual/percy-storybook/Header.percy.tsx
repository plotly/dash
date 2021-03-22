import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';
import DataTable from 'dash-table/dash/DataTable';

const setProps = () => {};

storiesOf('DashTable/Headers', module).add('multi header', () => (
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
));
