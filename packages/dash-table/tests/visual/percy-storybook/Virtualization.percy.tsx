import parser from 'papaparse';
import * as R from 'ramda';
import React from 'react';
import { storiesOf } from '@storybook/react';

import dataset from './../../../datasets/16zpallagi-25cols-100klines.csv';

import DataTable from 'dash-table/dash/DataTable';

const setProps = () => { };

const { data, meta } = parser.parse(dataset, { delimiter: ',', header: true });
const columns = R.map(i => ({ name: i, id: i }), meta.fields);

storiesOf('DashTable/Virtualization', module)
    .add('default', () => (<DataTable
        setProps={setProps}
        id='table'
        data={data}
        columns={columns}
        pagination_mode={false}
        virtualization={true}
        editable={true}
        n_fixed_rows={1}
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
    />));