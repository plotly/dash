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
const fixtureTests: any[] = [];
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
    fixtureTests.push(
        <div>{fixture.name}</div>,
        <DataTable {...Object.assign(fixture.props)} />
    );
});
storiesOf('DashTable/Fixtures', module).add('all fixtures', () => (
    <div>{...fixtureTests}</div>
));

import dataset from './../../assets/gapminder.csv';
const gapminder = parser.parse(dataset, {delimiter: ',', header: true});
import {TableAction, ExportFormat} from 'dash-table/components/Table/props';

storiesOf('DashTable/Basic', module).add('all variants', () => (
    <div>
        <div>one column, no data</div>
        <DataTable
            setProps={setProps}
            data={[]}
            columns={[{id: 'a', name: 'A'}]}
            sort_action={TableAction.None}
            editable={false}
            row_deletable={false}
            row_selectable={false}
        />
        <div>simple data</div>
        <DataTable
            data={gapminder.data}
            columns={R.map(i => ({name: i, id: i}), gapminder.meta.fields)}
            page_size={20}
        />
        <div>with 3 columns and 3 rows, not actionable</div>
        <DataTable
            setProps={setProps}
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
    </div>
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
const testColumns = JSON.parse(JSON.stringify(columnsA2J));
testColumns[2].hidden = true;

storiesOf('DashTable/Fixed Rows & Columns', module).add('all variants', () => (
    <div>
        <div>with 1 fixed row, 2 fixed columns</div>
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
        <div>with 1 fixed row</div>
        <DataTable
            setProps={setProps}
            data={dataA2J}
            columns={columnsA2J}
            fixed_rows={{headers: true}}
            row_deletable={true}
            row_selectable={true}
            style_data_conditional={style_data_conditional}
        />
        <div>with 2 fixed columns</div>
        <DataTable
            setProps={setProps}
            data={dataA2J.slice(0, 10)}
            columns={columnsA2J}
            fixed_columns={{headers: true}}
            row_deletable={true}
            row_selectable={true}
            style_data_conditional={style_data_conditional}
        />
        <div>with 2 fixed rows, 4 fixed columns and merged cells</div>
        <DataTable
            setProps={setProps}
            data={dataA2J}
            columns={mergedColumns}
            merge_duplicate_headers={true}
            fixed_columns={{headers: true, data: 4}}
            fixed_rows={{headers: true, data: 1}}
            style_data_conditional={style_data_conditional}
        />
        <div>2 fixed rows, 3 fixed cols, hidden cols and merged cells</div>
        <DataTable
            setProps={setProps}
            data={dataA2J}
            columns={mergedColumns}
            merge_duplicate_headers={true}
            fixed_columns={{headers: true, data: 3}}
            fixed_rows={{headers: true, data: 1}}
            style_data_conditional={style_data_conditional}
        />
    </div>
));

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

storiesOf('DashTable/Hidden Columns', module).add('all variants', () => (
    <div>
        <div>hides</div>
        <DataTable
            setProps={setProps}
            data={dataA2J.slice(0, 5)}
            columns={columnsA2J}
            hidden_columns={hiddenColumns}
            style_data_conditional={style_data_conditional}
        />
        <div>active cell</div>
        <DataTable
            setProps={setProps}
            data={dataA2J.slice(0, 5)}
            columns={columnsA2J}
            hidden_columns={hiddenColumns}
            active_cell={makeCell(1, 1, dataA2J, columnsA2J)}
            style_data_conditional={style_data_conditional}
        />
        <div>selected cells</div>
        <DataTable
            setProps={setProps}
            data={dataA2J.slice(0, 5)}
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
    </div>
));

storiesOf('DashTable/Sorting', module).add('all variants', () => (
    <div>
        <div>"a" ascending</div>
        <DataTable
            setProps={setProps}
            data={sparseData}
            columns={mergedColumns}
            sort_action={TableAction.Native}
            sort_by={[{column_id: 'a', direction: 'asc'}]}
            style_data_conditional={style_data_conditional}
        />
        <div>"a" descending</div>
        <DataTable
            setProps={setProps}
            data={sparseData}
            columns={mergedColumns}
            sort_action={TableAction.Native}
            sort_by={[{column_id: 'a', direction: 'desc'}]}
            style_data_conditional={style_data_conditional}
        />
        <div>"a" ascending -- empty string override</div>
        <DataTable
            setProps={setProps}
            data={sparseData}
            columns={mergedColumns}
            sort_action={TableAction.Native}
            sort_by={[{column_id: 'a', direction: 'asc'}]}
            sort_as_null={['']}
            style_data_conditional={style_data_conditional}
        />
        <div>"a" descending -- empty string override</div>
        <DataTable
            setProps={setProps}
            data={sparseData}
            columns={mergedColumns}
            sort_action={TableAction.Native}
            sort_by={[{column_id: 'a', direction: 'desc'}]}
            sort_as_null={['']}
            style_data_conditional={style_data_conditional}
        />
        <div>"a" descending -- empty string and 426 override</div>
        <DataTable
            setProps={setProps}
            data={sparseData}
            columns={mergedColumns}
            sort_action={TableAction.Native}
            sort_by={[{column_id: 'a', direction: 'desc'}]}
            sort_as_null={['', 426]}
            style_data_conditional={style_data_conditional}
        />
        <div>"a" ascending -- empty string and 426 override</div>
        <DataTable
            setProps={setProps}
            data={sparseData}
            columns={mergedColumns}
            sort_action={TableAction.Native}
            sort_by={[{column_id: 'a', direction: 'asc'}]}
            sort_as_null={['', 426]}
            style_data_conditional={style_data_conditional}
        />
    </div>
));

storiesOf('DashTable/Without id', module).add('all variants', () => (
    <div>
        <div>with 1 fixed row, 2 fixed columns</div>
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
        <div>with 1 fixed row, 2 fixed columns, set height and width</div>
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
        <div>with set height and width and colors</div>
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
        <div>Two tables with CSS props set</div>
        <DataTable
            setProps={setProps}
            data={dataA2J}
            columns={columnsA2J}
            fixed_columns={{headers: true}}
            fixed_rows={{headers: true}}
            row_deletable={true}
            row_selectable={true}
            style_table={{height: 300, width: 400}}
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
            style_table={{height: 300, width: 400}}
            css={[
                {
                    selector: '.dash-spreadsheet',
                    rule: 'border: 4px solid cyan'
                }
            ]}
        />
    </div>
));

storiesOf('DashTable/Export', module).add('all variants', () => (
    <div>
        <div>Export Button for xlsx file</div>
        <DataTable
            setProps={setProps}
            data={dataA2J.slice(0, 3)}
            columns={columnsA2J.slice(0, 10)}
            export_format={ExportFormat.Xlsx}
        />
        <div>Export Button for csv file</div>
        <DataTable
            setProps={setProps}
            data={dataA2J.slice(0, 3)}
            columns={columnsA2J.slice(0, 10)}
            export_format={ExportFormat.Xlsx}
        />
        <div>No export Button for file formatted not supported</div>
        <DataTable
            setProps={setProps}
            data={dataA2J.slice(0, 3)}
            columns={columnsA2J.slice(0, 10)}
            export_format={'json'}
        />
        <div>No export Button</div>
        <DataTable
            setProps={setProps}
            data={dataA2J.slice(0, 3)}
            columns={columnsA2J.slice(0, 10)}
            export_format={ExportFormat.None}
        />
    </div>
));
