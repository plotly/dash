import React from 'react';
import {storiesOf} from '@storybook/react';
import DataTable from 'dash-table/dash/DataTable';

const props = {
    setProps: () => {},
    data: [
        {a: 1, b: 2, c: 3},
        {a: 2, b: 4, c: 6},
        {a: 3, b: 6, c: 9}
    ],
    columns: [
        {id: 'a', name: 'A'},
        {id: 'b', name: 'B'},
        {id: 'c', name: 'C'}
    ],
    css: [{selector: 'td', rule: 'background-color: red !important;'}]
};

storiesOf('DashTable/CSS override', module)
    .add('leading _ without letter', () => <DataTable {...props} id={'_123'} />)
    .add('leading number', () => <DataTable {...props} id={'123'} />)
    .add('escaped characters', () => (
        <DataTable {...props} id={'`~!@#$%^&*()=+ \\|/.,:;\'"`?[]<>{}'} />
    ))
    .add('stringified object as id', () => (
        <DataTable {...props} id={"{ id: 3, group: 'A' }"} />
    ));
