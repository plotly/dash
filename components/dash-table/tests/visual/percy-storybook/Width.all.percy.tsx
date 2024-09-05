import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';
import random from 'core/math/random';
import DataTable from 'dash-table/dash/DataTable';

const setProps = () => {};

const columns = ['a', 'b', 'c'];

const data = (() => {
    const r = random(1);

    return R.range(0, 5).map(() =>
        ['a', 'b', 'c'].reduce((obj: any, key) => {
            obj[key] = Math.floor(r() * 1000);
            return obj;
        }, {})
    );
})();

const basePropsDflts = {
    setProps,
    fill_width: false,
    id: 'table',
    data
};

const propsDflts = Object.assign({}, basePropsDflts, {
    columns: columns.map(id => ({id: id, name: id.toUpperCase()}))
});

const basePropsWidth = {
    setProps,
    fill_width: false,
    id: 'table',
    data
};

const propsWidth = Object.assign({}, basePropsWidth, {
    columns: columns.map(id => ({id: id, name: id.toUpperCase(), width: 20}))
});

const basePropsMax = {
    setProps,
    fill_width: false,
    id: 'table',
    data,
    style_data_conditional: [{max_width: 10}]
};

const propsMax = Object.assign({}, basePropsMax, {
    columns: columns.map(id => ({id: id, name: id.toUpperCase()}))
});

const basePropsMin = {
    setProps,
    fill_width: false,
    id: 'table',
    data
};

const propsMin = Object.assign({}, basePropsMin, {
    columns: columns.map(id => ({id: id, name: id.toUpperCase()})),
    style_data_conditional: [{min_width: 100}]
});

const basePropsAll = {
    setProps,
    id: 'table',
    data,
    fill_width: false,
    style_data_conditional: [
        {width: '20px', min_width: '20px', max_width: '20px'}
    ]
};

const propsAll = Object.assign({}, basePropsAll, {
    columns: columns.map(id => ({id: id, name: id.toUpperCase()}))
});

const basePropsPct = {
    setProps,
    id: 'table',
    data
};

const propsPct = Object.assign({}, basePropsPct, {
    columns: columns.map(id => ({id: id, name: id.toUpperCase()})),
    style_cell: {
        width: '33%'
    },
    style_table: {
        width: '100%',
        min_width: '100%',
        max_width: '100%'
    },
    css: [
        {
            selector: '.dash-fixed-column',
            rule: 'width: 33%;'
        }
    ]
});

const makeVariants =
    (
        title: string,
        props:
            | ({
                  setProps: () => void;
                  id: string;
                  data: any[];
                  fill_width: boolean;
                  style_data_conditional: {
                      width: string;
                      min_width: string;
                      max_width: string;
                  }[];
              } & {columns: {id: string; name: string}[]})
            | (JSX.IntrinsicAttributes &
                  JSX.IntrinsicClassAttributes<DataTable> &
                  Readonly<any> &
                  Readonly<{children?: React.ReactNode}>)
    ) =>
    () =>
        (
            <div>
                <div style={{fontWeight: 'bold'}}>{title}</div>
                <div>without frozen columns or rows</div>
                <DataTable {...props} />
                <div>with frozen rows</div>
                <DataTable {...props} fixed_rows={{headers: true}} />
                <div>with frozen columns</div>
                <DataTable {...props} fixed_columns={{headers: true}} />
                <div>with frozen rows and frozen columns</div>
                <DataTable
                    {...props}
                    fixed_columns={{headers: true}}
                    fixed_rows={{headers: true}}
                />
            </div>
        );

storiesOf('DashTable/Width -', module)
    .add('defaults', makeVariants('defaults', propsDflts))
    .add('width only', makeVariants('width only', propsWidth))
    .add('maxWidth only', makeVariants('maxWidth only', propsMax))
    .add('minWidth only', makeVariants('minWidth only', propsMin))
    .add(
        'width, minWidth, maxWidth',
        makeVariants('width, minWidth, maxWidth', propsAll)
    )
    .add('percentage', makeVariants('percentage', propsPct));
