import React from 'react';
import {storiesOf} from '@storybook/react';

import DataTable from 'dash-table/dash/DataTable';
import {TableAction} from 'dash-table/components/Table/props';

const actions = [TableAction.Native, TableAction.Custom];

const setProps = () => {};

const elements: [React.ReactNode?] = [];

actions.forEach(filter => {
    actions.forEach(sort => {
        actions.forEach(page => {
            elements.push(
                <div
                    style={{marginTop: '10px'}}
                >{`filter=${filter}, sorting=${sort}, pagination=${page}`}</div>
            );
            elements.push(
                <DataTable
                    columns={[
                        {name: 'A', id: 'a'},
                        {name: 'B', id: 'b'}
                    ]}
                    data={[{a: 1, b: 2}]}
                    filter_action={filter}
                    sort_action={sort}
                    page_action={page}
                    setProps={setProps}
                />
            );
        });
    });
});

storiesOf('DashTable/Props Validation', module).add('all variants', () => (
    <div style={{width: '500px'}}>{elements}</div>
));
