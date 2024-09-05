import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';
import random from 'core/math/random';
import DataTable from 'dash-table/dash/DataTable';
import {TableAction} from 'dash-table/components/Table/props';

const setProps = () => {};

const data = (() => {
    const r = random(1);

    return R.range(0, 5).map(() =>
        ['a', 'b', 'c'].reduce((obj: any, key) => {
            obj[key] = Math.floor(r() * 1000);
            return obj;
        }, {})
    );
})();

const props = {
    setProps,
    data: data,
    filter_action: TableAction.Native,
    style_cell: {
        width: 100,
        min_width: 100,
        max_width: 100
    }
};

storiesOf('DashTable/Filtering', module).add('all variants', () => (
    <div>
        <div>with a single column</div>
        <DataTable
            {...props}
            columns={['a'].map(id => ({id: id, name: id.toUpperCase()}))}
        />
        <div>with multiple columns</div>
        <DataTable
            {...props}
            columns={['a', 'b', 'c'].map(id => ({
                id: id,
                name: id.toUpperCase()
            }))}
        />
    </div>
));
