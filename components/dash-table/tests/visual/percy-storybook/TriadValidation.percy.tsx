import React from 'react';
import {storiesOf} from '@storybook/react';

import DataTable from 'dash-table/dash/DataTable';
import {TableAction} from 'dash-table/components/Table/props';

const actions = [TableAction.Native, TableAction.Custom];

const setProps = () => {};

let stories = storiesOf('DashTable/Props Validation', module);

actions.forEach(filter => {
    actions.forEach(sort => {
        actions.forEach(page => {
            stories = stories.add(
                `filter=${filter}, sorting=${sort}, pagination=${page}`,
                () => (
                    <DataTable
                        filter_action={filter}
                        sort_action={sort}
                        page_action={page}
                        setProps={setProps}
                    />
                )
            );
        });
    });
});
