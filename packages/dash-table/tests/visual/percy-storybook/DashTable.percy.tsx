import React from 'react';
import { storiesOf } from '@storybook/react';
import DashTable from 'dash-table/components/Table';

import fixtures from './fixtures';

const setProps = () => { };

storiesOf('DashTable/Without Data', module)
    .add('with 1 column', () => (<DashTable
        setProps={setProps}
        id='table'
        dataframe={[]}
        columns={[{ id: 'a', name: 'A' }]}
        sortable={false}
        editable={false}
        row_deletable={false}
        row_selectable={false}
    />));

const fixtureStories = storiesOf('DashTable/Fixtures');
fixtures.forEach(fixture => fixtureStories.add(fixture.name, () => (<DashTable {...Object.assign(fixture.props)} />)));

storiesOf('DashTable/With Data')
    .add('with 3 columns and 3 rows, not actionable', () => (<DashTable
        setProps={setProps}
        id='table'
        dataframe={[
            { a: 1, b: 2, c: 3 },
            { a: 11, b: 12, c: 13 },
            { a: 21, b: 22, c: 23 }
        ]}
        columns={[
            { id: 'a', name: 'A', width: '100px' },
            { id: 'b', name: 'B', width: '50px' },
            { id: 'c', name: 'C', width: '200px' }
        ]}
        editable={false}
        sortable={false}
        row_deletable={false}
        row_selectable={false}
    />));