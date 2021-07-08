import parser from 'papaparse';
import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';

import random from 'core/math/random';
import DataTable from 'dash-table/dash/DataTable';
import fixtures from './fixtures';

const setProps = () => {};

function makeCell(row: number, column: number, data: any[], columns: any[]) {
    const cell: any = {
        row,
        column,
        column_id: columns[column].id
    };
    const rowID = data[row].id;
    if (rowID !== undefined) {
        cell.row_id = rowID;
    }
    return cell;
}

function makeSelection(coords: any[], data: any[], columns: any[]) {
    return coords.map(pair => makeCell(pair[0], pair[1], data, columns));
}

// Legacy: Tests previously run in Python
const fixtureStories = storiesOf('DashTable/Fixtures', module);
fixtures.forEach(fixture => {
    // update active and selected cells for the new cell object format
    const {data, columns, active_cell, selected_cells} = fixture.props;
    if (Array.isArray(active_cell)) {
        fixture.props.active_cell = makeCell(
            active_cell[0],
            active_cell[1],
            data as any[],
            columns as any[]
        );
    }
    if (Array.isArray(selected_cells) && Array.isArray(selected_cells[0])) {
        fixture.props.selected_cells = makeSelection(
            selected_cells,
            data as any[],
            columns as any[]
        );
    }

    fixtureStories.add(fixture.name, () => (
        <DataTable {...Object.assign(fixture.props)} />
    ));
});

import dataset from './../../assets/gapminder.csv';
import {TableAction, ExportFormat} from 'dash-table/components/Table/props';

storiesOf('DashTable/Without Data', module).add('with 1 column', () => (
    <DataTable
        setProps={setProps}
        id='table'
        data={[]}
        columns={[{id: 'a', name: 'A'}]}
        sort_action={TableAction.None}
        editable={false}
        row_deletable={false}
        row_selectable={false}
    />
));

storiesOf('DashTable/With Data', module)
    .add('simple', () => {
        const result = parser.parse(dataset, {delimiter: ',', header: true});

        return (
            <DataTable
                id='table'
                data={result.data}
                columns={R.map(i => ({name: i, id: i}), result.meta.fields)}
            />
        );
    })
    .add('with 3 columns and 3 rows, not actionable', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={[
                {a: 1, b: 2, c: 3},
                {a: 11, b: 12, c: 13},
                {a: 21, b: 22, c: 23}
            ]}
            columns={[
                {id: 'a', name: 'A'},
                {id: 'b', name: 'B'},
                {id: 'c', name: 'C'}
            ]}
            editable={false}
            sort_action={TableAction.None}
            row_deletable={false}
            row_selectable={false}
            style_data_conditional={[
                {if: {column_id: 'a'}, width: '100px'},
                {if: {column_id: 'b'}, width: '50px'},
                {if: {column_id: 'c'}, width: '200px'}
            ]}
        />
    ));

const columnsA2J = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'].map(
    id => ({id: id, name: id.toUpperCase()})
);

const idMap: {[key: string]: string} = {
    a: 'A',
    b: 'A',
    c: 'B',
    d: 'B',
    e: 'C',
    f: 'C',
    g: 'C',
    h: 'D',
    i: 'D',
    j: 'D'
};

const mergedColumns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'].map(
    id => ({id: id, name: [idMap[id], id.toUpperCase()]})
);

const dataA2J = (() => {
    const r = random(1);

    return R.range(0, 100).map(() =>
        ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'].reduce(
            (obj: any, key) => {
                obj[key] = Math.floor(r() * 1000);
                return obj;
            },
            {}
        )
    );
})();

const style_data_conditional = [{width: '100px'}];

storiesOf('DashTable/Fixed Rows & Columns', module)
    .add('with 1 fixed row, 2 fixed columns', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={dataA2J}
            columns={columnsA2J}
            fixed_columns={{headers: true}}
            fixed_rows={{headers: true}}
            row_deletable={true}
            row_selectable={true}
            style_data_conditional={style_data_conditional}
        />
    ))
    .add('with 1 fixed row', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={dataA2J}
            columns={columnsA2J}
            fixed_rows={{headers: true}}
            row_deletable={true}
            row_selectable={true}
            style_data_conditional={style_data_conditional}
        />
    ))
    .add('with 2 fixed columns', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={dataA2J}
            columns={columnsA2J}
            fixed_columns={{headers: true}}
            row_deletable={true}
            row_selectable={true}
            style_data_conditional={style_data_conditional}
        />
    ))
    .add('with 2 fixed rows, 4 fixed columns and merged cells', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={dataA2J}
            columns={mergedColumns}
            merge_duplicate_headers={true}
            fixed_columns={{headers: true, data: 4}}
            fixed_rows={{headers: true, data: 1}}
            style_data_conditional={style_data_conditional}
        />
    ))
    .add(
        'with 2 fixed rows, 3 fixed columns, hidden columns and merged cells',
        () => {
            const testColumns = JSON.parse(JSON.stringify(columnsA2J));
            testColumns[2].hidden = true;

            return (
                <DataTable
                    setProps={setProps}
                    id='table'
                    data={dataA2J}
                    columns={mergedColumns}
                    merge_duplicate_headers={true}
                    fixed_columns={{headers: true, data: 3}}
                    fixed_rows={{headers: true, data: 1}}
                    style_data_conditional={style_data_conditional}
                />
            );
        }
    );

const sparseData = (() => {
    const r = random(1);

    return R.range(0, 10).map(index =>
        ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'].reduce(
            (obj: any, key) => {
                obj[key] = index <= 5 ? '' : Math.floor(r() * 1000);
                return obj;
            },
            {}
        )
    );
})();

const hiddenColumns = columnsA2J
    .map(c => c.id)
    .filter((_, index) => index % 2 === 0);

storiesOf('DashTable/Hidden Columns', module)
    .add('hides', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={dataA2J}
            columns={columnsA2J}
            hidden_columns={hiddenColumns}
            style_data_conditional={style_data_conditional}
        />
    ))
    .add('active cell', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={dataA2J}
            columns={columnsA2J}
            hidden_columns={hiddenColumns}
            active_cell={makeCell(1, 1, dataA2J, columnsA2J)}
            style_data_conditional={style_data_conditional}
        />
    ))
    .add('selected cells', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={dataA2J}
            columns={columnsA2J}
            hidden_columns={hiddenColumns}
            active_cell={makeCell(1, 1, dataA2J, columnsA2J)}
            selected_cells={makeSelection(
                [
                    [1, 1],
                    [1, 2],
                    [2, 1],
                    [2, 2]
                ],
                dataA2J,
                columnsA2J
            )}
            style_data_conditional={style_data_conditional}
        />
    ));

storiesOf('DashTable/Sorting', module)
    .add('"a" ascending', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={sparseData}
            columns={mergedColumns}
            sort_action={TableAction.Native}
            sort_by={[{column_id: 'a', direction: 'asc'}]}
            style_data_conditional={style_data_conditional}
        />
    ))
    .add('"a" descending', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={sparseData}
            columns={mergedColumns}
            sort_action={TableAction.Native}
            sort_by={[{column_id: 'a', direction: 'desc'}]}
            style_data_conditional={style_data_conditional}
        />
    ))
    .add('"a" ascending -- empty string override', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={sparseData}
            columns={mergedColumns}
            sort_action={TableAction.Native}
            sort_by={[{column_id: 'a', direction: 'asc'}]}
            sort_as_null={['']}
            style_data_conditional={style_data_conditional}
        />
    ))
    .add('"a" descending -- empty string override', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={sparseData}
            columns={mergedColumns}
            sort_action={TableAction.Native}
            sort_by={[{column_id: 'a', direction: 'desc'}]}
            sort_as_null={['']}
            style_data_conditional={style_data_conditional}
        />
    ))
    .add('"a" descending -- empty string & 426 override', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={sparseData}
            columns={mergedColumns}
            sort_action={TableAction.Native}
            sort_by={[{column_id: 'a', direction: 'desc'}]}
            sort_as_null={['', 426]}
            style_data_conditional={style_data_conditional}
        />
    ))
    .add('"a" ascending -- empty string and 426 override', () => (
        <DataTable
            setProps={setProps}
            id='table'
            data={sparseData}
            columns={mergedColumns}
            sort_action={TableAction.Native}
            sort_by={[{column_id: 'a', direction: 'asc'}]}
            sort_as_null={['', 426]}
            style_data_conditional={style_data_conditional}
        />
    ));
storiesOf('DashTable/Without id', module)
    .add('with 1 fixed row, 2 fixed columns', () => (
        <DataTable
            setProps={setProps}
            data={dataA2J}
            columns={columnsA2J}
            fixed_columns={{headers: true}}
            fixed_rows={{headers: true}}
            row_deletable={true}
            row_selectable={true}
            style_data_conditional={style_data_conditional}
        />
    ))
    .add('with 1 fixed row, 2 fixed columns, set height and width', () => (
        <DataTable
            setProps={setProps}
            data={dataA2J}
            columns={columnsA2J}
            fixed_columns={{headers: true}}
            fixed_rows={{headers: true}}
            row_deletable={true}
            row_selectable={true}
            style_table={{height: 500, width: 200}}
            style_data_conditional={style_data_conditional}
        />
    ))
    .add('with set height and width and colors', () => (
        <DataTable
            setProps={setProps}
            data={dataA2J}
            columns={columnsA2J}
            fixed_columns={{headers: true}}
            fixed_rows={{headers: true}}
            row_deletable={true}
            row_selectable={true}
            style_table={{height: 500, width: 200}}
            style_data_conditional={[
                {
                    if: {column_id: 'a'},
                    background_color: 'yellow'
                }
            ]}
        />
    ))
    .add('Two tables with CSS props set', () => (
        <div>
            <DataTable
                setProps={setProps}
                data={dataA2J}
                columns={columnsA2J}
                fixed_columns={{headers: true}}
                fixed_rows={{headers: true}}
                row_deletable={true}
                row_selectable={true}
                style_table={{height: 500, width: 400}}
                css={[
                    {
                        selector: '.dash-spreadsheet',
                        rule: 'border: 4px solid hotpink'
                    }
                ]}
            />
            <DataTable
                setProps={setProps}
                data={dataA2J}
                columns={columnsA2J}
                fixed_columns={{headers: true}}
                fixed_rows={{headers: true}}
                row_deletable={true}
                row_selectable={true}
                style_table={{height: 500, width: 400}}
                css={[
                    {
                        selector: '.dash-spreadsheet',
                        rule: 'border: 4px solid cyan'
                    }
                ]}
            />
        </div>
    ));

storiesOf('DashTable/Export', module)
    .add('Export Button for xlsx file', () => (
        <DataTable
            setProps={setProps}
            data={dataA2J.slice(0, 10)}
            columns={columnsA2J.slice(0, 10)}
            export_format={ExportFormat.Xlsx}
        />
    ))
    .add('Export Button for csv file', () => (
        <DataTable
            setProps={setProps}
            data={dataA2J.slice(0, 10)}
            columns={columnsA2J.slice(0, 10)}
            export_format={ExportFormat.Xlsx}
        />
    ))
    .add('No export Button for file formatted not supported', () => (
        <DataTable
            setProps={setProps}
            data={dataA2J.slice(0, 10)}
            columns={columnsA2J.slice(0, 10)}
            export_format={'json'}
        />
    ))
    .add('No export Button', () => (
        <DataTable
            setProps={setProps}
            data={dataA2J.slice(0, 10)}
            columns={columnsA2J.slice(0, 10)}
            export_format={ExportFormat.None}
        />
    ));
