import React from 'react';
import { storiesOf } from '@storybook/react';
import DashTable from 'dash-table/components/Table';

const state = {
    tableProps: {
        id: 'table',
        dataframe: [],
        columns: [{ id: 'a', name: 'A' }],
        editable: true,
        sortable: false,
        sort: [],
        merge_duplicate_headers: true,
        row_deletable: true,
        row_selectable: 'single'
    },
    selectedFixture: null
};

const setProps = () => {

};

storiesOf('DashTable', module)
    .add('with defaults', () => (<DashTable
        setProps={setProps}
        {...state.tableProps}
    />));