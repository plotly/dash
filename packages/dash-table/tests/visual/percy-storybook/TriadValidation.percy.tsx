import React from 'react';
import { storiesOf } from '@storybook/react';

import DataTable from 'dash-table/DataTable';

const filteringValues = ['fe', 'be'];
const sortingValues = ['fe', 'be'];
const paginationValues = ['fe', 'be'];

const setProps = () => { };

let stories = storiesOf('DashTable/Props Validation', module);

filteringValues.forEach(filter => {
    sortingValues.forEach(sort => {
        paginationValues.forEach(page => {
            stories = stories.add(`filter=${filter}, sorting=${sort}, pagination=${page}`, () => (<DataTable
                filtering={filter}
                sorting={sort}
                pagination_mode={page}
                setProps={setProps}
            />));
        });
    });
});