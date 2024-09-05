import parser from 'papaparse';
import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';

import dataset from './../../assets/16zpallagi-25cols-100klines.csv';

import DataTable from 'dash-table/dash/DataTable';
import {TableAction} from 'dash-table/components/Table/props';

const setProps = () => {};

const {data, meta} = parser.parse(dataset, {delimiter: ',', header: true});
const columns = R.map(i => ({name: i, id: i}), meta.fields);

storiesOf('DashTable/Virtualization', module).add('default', () => (
    <DataTable
        setProps={setProps}
        id='table'
        data={data}
        columns={columns}
        page_action={TableAction.None}
        virtualization={true}
        editable={true}
        fixed_rows={{headers: true}}
        style_table={{
            height: 800,
            max_height: 800,
            width: 1300,
            max_width: 1300
        }}
        style_data={{
            width: 50,
            max_width: 50,
            min_width: 50
        }}
    />
));
