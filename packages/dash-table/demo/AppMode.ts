import * as R from 'ramda';

import Environment from 'core/environment';

import { generateMockData, IDataMock, generateSpaceMockData } from './data';
import {
    ContentStyle,
    PropsWithDefaults,
    ChangeAction,
    ChangeFailure,
    IVisibleColumn
} from 'dash-table/components/Table/props';
import { TooltipSyntax } from 'dash-table/tooltips/props';

export enum AppMode {
    Default = 'default',
    FixedVirtualized = 'fixed,virtualized',
    ReadOnly = 'readonly',
    ColumnsInSpace = 'columnsInSpace',
    Tooltips = 'tooltips',
    Typed = 'typed',
    Virtualized = 'virtualized'
}

export const ReadWriteModes = [
    AppMode.Default,
    AppMode.FixedVirtualized,
    AppMode.Virtualized
];

function getBaseTableProps(mock: IDataMock) {
    return {
        id: 'table',
        columns: mock.columns.map((col: any) => R.merge(col, {
            name: col.name || col.id,
            on_change: {
                action: ChangeAction.None
            },
            editable_name: true,
            deletable: true
        })),
        column_static_dropdown: [
            {
                id: 'bbb',
                dropdown: ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'].map(i => ({
                    label: i,
                    value: i
                }))
            }
        ],
        pagination_mode: false,
        style_table: {
            max_height: '800px',
            height: '800px',
            max_width: '1000px',
            width: '1000px'
        },
        style_data_conditional: [
            { max_width: 150, min_width: 150, width: 150 },
            { if: { column_id: 'rows' }, max_width: 60, min_width: 60, width: 60 },
            { if: { column_id: 'bbb' }, max_width: 200, min_width: 200, width: 200 },
            { if: { column_id: 'bbb-readonly' }, max_width: 200, min_width: 200, width: 200 }
        ]
    };
}

function getDefaultState(
    generateData: Function = generateMockData
): {
    filter: string,
    tableProps: Partial<PropsWithDefaults>
} {
    const mock = generateData(5000);

    return {
        filter: '',
        tableProps: R.merge(getBaseTableProps(mock), {
            data: mock.data,
            editable: true,
            sorting: true,
            n_fixed_rows: 3,
            n_fixed_columns: 2,
            merge_duplicate_headers: false,
            row_deletable: true,
            row_selectable: 'single',
            content_style: ContentStyle.Fit,
            pagination_mode: 'fe'
        }) as Partial<PropsWithDefaults>
    };
}

function getReadonlyState() {
    const state = getDefaultState();
    state.tableProps.editable = false;
    state.tableProps.row_deletable = false;

    R.forEach(column => {
        column.editable = false;
    }, state.tableProps.columns || []);

    return state;
}

function getSpaceInColumn() {
    const state = getDefaultState(generateSpaceMockData);
    state.tableProps.filtering = true;

    return state;
}

function getTooltipsState() {
    const state = getDefaultState();

    state.tableProps.tooltips = {
        ccc: [
            { type: TooltipSyntax.Markdown, value: `### Go Proverb\nThe enemy's key point is yours` },
            { type: TooltipSyntax.Markdown, value: `### Go Proverb\nPlay on the point of symmetry` },
            { type: TooltipSyntax.Markdown, value: `### Go Proverb\nSente gains nothing` },
            { type: TooltipSyntax.Text, value: `Beware of going back to patch up` },
            { type: TooltipSyntax.Text, value: `When in doubt, Tenuki` },
            `People in glass houses shouldn't throw stones`
        ]
    };
    state.tableProps.column_static_tooltip = {
        ccc: { type: TooltipSyntax.Text, value: `There is death in the hane`, delay: 1000, duration: 5000 },
        ddd: { type: TooltipSyntax.Markdown, value: `Hane, Cut, Placement` },
        rows: `Learn the eyestealing tesuji`
    };
    state.tableProps.column_conditional_tooltips = [{
        if: {
            column_id: 'aaa-readonly',
            filter: `aaa is prime`
        },
        type: TooltipSyntax.Markdown,
        value: `### Go Proverbs\nCapture three to get an eye`
    }, {
        if: {
            column_id: 'bbb-readonly',
            row_index: 'odd'
        },
        type: TooltipSyntax.Markdown,
        value: `### Go Proverbs\nSix die but eight live`
    }, {
        if: {
            column_id: 'bbb-readonly'
        },
        delay: 1000,
        duration: 5000,
        type: TooltipSyntax.Markdown,
        value: `### Go Proverbs\nUrgent points before big points\n![Sensei](https://senseis.xmp.net/images/stone-hello.png)`
    }];

    return state;
}

function getTypedState() {
    const state = getDefaultState();

    R.forEach(column => {
        (column as IVisibleColumn).on_change = {
            action: ChangeAction.Coerce,
            failure: ChangeFailure.Reject
        };
    }, state.tableProps.columns || []);

    return state;
}

function getVirtualizedState() {
    const mock = generateMockData(5000);

    return {
        filter: '',
        tableProps: R.merge(getBaseTableProps(mock), {
            data: mock.data,
            editable: true,
            sorting: true,
            merge_duplicate_headers: false,
            row_deletable: true,
            row_selectable: 'single',
            content_style: 'fit',
            virtualization: true
        })
    };
}

function getFixedVirtualizedState() {
    const mock = generateMockData(5000);

    return {
        filter: '',
        tableProps: R.merge(getBaseTableProps(mock), {
            data: mock.data,
            editable: true,
            sorting: true,
            n_fixed_rows: 3,
            n_fixed_columns: 2,
            merge_duplicate_headers: false,
            row_deletable: true,
            row_selectable: 'single',
            content_style: 'fit',
            virtualization: true
        })
    };
}

function getState() {
    const mode = Environment.searchParams.get('mode');

    switch (mode) {
        case AppMode.FixedVirtualized:
            return getFixedVirtualizedState();
        case AppMode.ReadOnly:
            return getReadonlyState();
        case AppMode.ColumnsInSpace:
            return getSpaceInColumn();
        case AppMode.Tooltips:
            return getTooltipsState();
        case AppMode.Virtualized:
            return getVirtualizedState();
        case AppMode.Typed:
            return getTypedState();
        case AppMode.Default:
        default:
            return getDefaultState();
    }
}
export default getState();
