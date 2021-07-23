import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';
import random from 'core/math/random';
import DataTable from 'dash-table/dash/DataTable';

const setProps = () => {};

const columns = ['a', 'b', 'c'].map(id => ({id: id, name: id.toUpperCase()}));

const data = (() => {
    const r = random(1);

    return R.range(0, 5).map(() =>
        ['a', 'b', 'c'].reduce((obj: any, key) => {
            obj[key] = Math.floor(r() * 1000);
            return obj;
        }, {})
    );
})();

const columns2 = ['a', 'b', 'c', 'd', 'e', 'f'].map(id => ({
    id: id,
    name: id.toUpperCase()
}));

const data2 = (() => {
    const r = random(1);

    return R.range(0, 50).map(() =>
        ['a', 'b', 'c', 'd', 'e', 'f'].reduce((obj: any, key) => {
            obj[key] = Math.floor(r() * 1000);
            return obj;
        }, {})
    );
})();

const style_table = {
    height: 500,
    width: 500
};

const style_data_conditional = [
    {
        if: {},
        width: 100,
        minWidth: 100,
        maxWidth: 100
    }
];

export const BORDER_PROPS_DEFAULTS = {
    setProps,
    id: 'table',
    data: data,
    columns,
    style_data_conditional,
    style_table
};

const props2 = {
    setProps,
    id: 'table',
    data: data2,
    columns: columns2,
    style_data_conditional,
    style_table
};

storiesOf('DashTable/Border (available space not filled)', module)
    .add('with no frozen rows and no frozen columns', () => (
        <DataTable {...BORDER_PROPS_DEFAULTS} />
    ))
    .add('with frozen rows and no frozen columns', () => (
        <DataTable {...BORDER_PROPS_DEFAULTS} fixed_rows={{headers: true}} />
    ))
    .add('with no frozen rows and frozen columns', () => (
        <DataTable
            {...BORDER_PROPS_DEFAULTS}
            fixed_columns={{headers: true, data: 1}}
        />
    ))
    .add('with frozen rows and frozen columns', () => (
        <DataTable
            {...BORDER_PROPS_DEFAULTS}
            fixed_columns={{headers: true, data: 1}}
            fixed_rows={{headers: true}}
        />
    ));

storiesOf('DashTable/Border (available space filled)', module)
    .add('with no frozen rows and no frozen columns', () => (
        <DataTable {...props2} />
    ))
    .add('with frozen rows and no frozen columns', () => (
        <DataTable {...props2} fixed_rows={{headers: true}} />
    ))
    .add('with no frozen rows and frozen columns', () => (
        <DataTable
            {...props2}
            DataTable
            fixed_columns={{headers: true, data: 1}}
        />
    ))
    .add('with frozen rows and frozen columns', () => (
        <DataTable
            {...props2}
            fixed_columns={{headers: true, data: 1}}
            fixed_rows={{headers: true}}
        />
    ));

const props3 = Object.assign({}, BORDER_PROPS_DEFAULTS, {
    style_as_list_view: true
});

const props4 = Object.assign({}, props2, {
    style_as_list_view: true
});

storiesOf(
    'DashTable/ListView style, Border (available space not filled)',
    module
)
    .add('with no frozen rows and no frozen columns', () => (
        <DataTable {...props3} />
    ))
    .add('with frozen rows and no frozen columns', () => (
        <DataTable {...props3} fixed_rows={{headers: true}} />
    ))
    .add('with no frozen rows and frozen columns', () => (
        <DataTable {...props3} fixed_columns={{headers: true, data: 1}} />
    ))
    .add('with frozen rows and frozen columns', () => (
        <DataTable
            {...props3}
            fixed_columns={{headers: true, data: 1}}
            fixed_rows={{headers: true}}
        />
    ));

storiesOf('DashTable/ListView style, Border (available space filled)', module)
    .add('with no frozen rows and no frozen columns', () => (
        <DataTable {...props4} />
    ))
    .add('with frozen rows and no frozen columns', () => (
        <DataTable {...props4} fixed_rows={{headers: true}} />
    ))
    .add('with no frozen rows and frozen columns', () => (
        <DataTable {...props4} fixed_columns={{headers: true, data: 1}} />
    ))
    .add('with frozen rows and frozen columns', () => (
        <DataTable
            {...props4}
            fixed_columns={{headers: true, data: 1}}
            fixed_rows={{headers: true}}
        />
    ));

storiesOf('DashTable/Rounded Border', module).add('with rounded border', () => (
    <DataTable
        {...{
            setProps,
            id: 'table',
            data: data,
            columns,
            style_table: {
                border: '1px solid red',
                borderRadius: '15px',
                overflow: 'hidden'
            }
        }}
    />
));
