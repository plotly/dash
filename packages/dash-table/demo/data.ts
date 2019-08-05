/* eslint no-magic-numbers: 0 */
import * as R from 'ramda';
import { ColumnType } from 'dash-table/components/Table/props';

const N_DATA = 100000;

export interface IDataMock {
    columns: any[];
    data: any[];
}

export const generateMockData = (rows: number) => unpackIntoColumnsAndData([
    {
        id: 'rows',
        type: ColumnType.Numeric,
        editable: false,
        data: gendata(i => i, rows)
    },

    {
        id: 'ccc',
        name: ['City', 'Canada', 'Toronto'],
        type: ColumnType.Numeric,
        data: gendata(i => i, rows)
    },

    {
        id: 'ddd',
        name: ['City', 'Canada', 'Montréal'],
        type: ColumnType.Numeric,
        data: gendata(i => i * 100, rows)
    },

    {
        id: 'eee',
        name: ['City', 'America', 'New York City'],
        type: ColumnType.Numeric,
        data: gendata(i => i, rows)
    },

    {
        id: 'fff',
        name: ['City', 'America', 'Boston'],
        type: ColumnType.Numeric,
        data: gendata(i => i + 1, rows)
    },

    {
        id: 'ggg',
        name: ['City', 'France', 'Paris'],
        type: ColumnType.Numeric,
        editable: true,
        data: gendata(i => i * 10, rows)
    },

    {
        id: 'bbb',
        name: ['', 'Weather', 'Climate'],
        type: ColumnType.Text,
        presentation: 'dropdown',
        data: gendata(
            i => ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'][i % 4],
            rows
        )
    },

    {
        id: 'bbb-readonly',
        name: ['', 'Weather', 'Climate-RO'],
        type: ColumnType.Text,
        presentation: 'dropdown',
        editable: false,
        data: gendata(
            i => ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'][i % 4],
            rows
        )
    },

    {
        id: 'aaa',
        name: ['', 'Weather', 'Temperature'],
        type: ColumnType.Numeric,
        data: gendata(i => i + 1, rows)
    },

    {
        id: 'aaa-readonly',
        name: ['', 'Weather', 'Temperature-RO'],
        type: ColumnType.Numeric,
        presentation: 'dropdown',
        editable: false,
        data: gendata(i => i + 1, rows)
    }
]);

export const generateSpaceMockData = (rows: number) => unpackIntoColumnsAndData([
    {
        id: 'rows',
        type: ColumnType.Numeric,
        editable: false,
        data: gendata(i => i, rows)
    },

    {
        id: 'c cc',
        name: ['City', 'Canada', 'Toronto'],
        type: ColumnType.Numeric,
        data: gendata(i => i, rows)
    },

    {
        id: 'd:dd',
        name: ['City', 'Canada', 'Montréal'],
        type: ColumnType.Numeric,
        data: gendata(i => i * 100, rows)
    },

    {
        id: 'e-ee',
        name: ['City', 'America', 'New York City'],
        type: ColumnType.Numeric,
        data: gendata(i => i, rows)
    },

    {
        id: 'f_ff',
        name: ['City', 'America', 'Boston'],
        type: ColumnType.Numeric,
        data: gendata(i => i + 1, rows)
    },

    {
        id: 'g.gg',
        name: ['City', 'France', 'Paris'],
        type: ColumnType.Numeric,
        editable: true,
        data: gendata(i => i * 10, rows)
    },

    {
        id: 'b+bb',
        name: ['', 'Weather', 'Climate'],
        type: ColumnType.Text,
        presentation: 'dropdown',
        data: gendata(
            i => ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'][i % 4],
            rows
        )
    }
]);

export const mockDataSimple = (rows: number) => unpackIntoColumnsAndData([
    {
        id: 'aaa',
        name: 'Temperature',
        type: ColumnType.Numeric,
        data: gendata(i => i + 1, rows)
    },

    {
        id: 'bbb',
        name: 'Climate',
        type: ColumnType.Text,
        presentation: 'dropdown',
        data: gendata(
            i => ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'][i % 4],
            rows
        )
    }
]);

export const miniData = unpackIntoColumnsAndData([
    {
        id: 'aaa', name: 'cheese', data: [1, 2, 3]
    },
    {
        id: 'bbb', name: 'tomato', data: [3, 2, 1]
    }
]);

function unpackIntoColumnsAndData(columns: any[]): IDataMock {
    const mocked: any = { columns: [], data: [] };

    columns.forEach(col => {
        col.data.forEach((v: any, i: number) => {
            if (!mocked.data[i]) {
                mocked.data[i] = {};
            }
            mocked.data[i][col.id] = v;
        });
        mocked.columns.push(R.dissoc('data', col));
    });
    return mocked;
}

function gendata(func: (i: number) => any, ndata = N_DATA) {
    return R.range(1, ndata).map(func);
}
