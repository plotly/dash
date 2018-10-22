/* eslint no-magic-numbers: 0 */
import * as R from 'ramda';

const N_DATA = 5000;

export const mockData = unpackIntoColumnsAndData([
    {
        id: 'rows',
        type: 'numeric',
        editable: false,
        data: gendata(i => i)
    },

    {
        id: 'ccc',
        name: ['City', 'Canada', 'Toronto'],
        type: 'numeric',
        data: gendata(i => i),
    },

    {
        id: 'ddd',
        name: ['City', 'Canada', 'Montréal'],
        type: 'numeric',
        data: gendata(i => i * 100),
    },

    {
        id: 'eee',
        name: ['City', 'America', 'New York City'],
        type: 'numeric',
        data: gendata(i => i),
    },

    {
        id: 'fff',
        name: ['City', 'America', 'Boston'],
        type: 'numeric',
        data: gendata(i => i + 1)
    },

    {
        id: 'ggg',
        name: ['City', 'France', 'Paris'],
        type: 'numeric',
        editable: true,
        data: gendata(i => i * 10),
    },

    {
        id: 'bbb',
        name: ['', 'Weather', 'Climate'],
        type: 'dropdown',
        clearable: true,
        data: gendata(
            i => ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'][i % 4]
        )
    },

    {
        id: 'bbb-readonly',
        name: ['', 'Weather', 'Climate-RO'],
        type: 'dropdown',
        editable: false,
        data: gendata(
            i => ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'][i % 4]
        )
    },

    {
        id: 'aaa',
        name: ['', 'Weather', 'Temperature'],
        type: 'numeric',
        data: gendata(i => i + 1),
    },

    {
        id: 'aaa-readonly',
        name: ['', 'Weather', 'Temperature-RO'],
        type: 'numeric',
        editable: false,
        data: gendata(i => i + 1),
    }
]);

export const mockDataSimple = unpackIntoColumnsAndData([
    {
        id: 'aaa',
        name: 'Temperature',
        type: 'numeric',
        data: gendata(i => i + 1),
    },

    {
        id: 'bbb',
        name: 'Climate',
        type: 'numeric',
        options: ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'].map(i => ({
            label: i,
            value: i,
        })),
        clearable: true,
        data: gendata(
            i => ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'][i % 4]
        ),
    },
]);

export const miniData = unpackIntoColumnsAndData([
    {
        id: 'aaa', name: 'cheese', data: [1, 2, 3]
    },
    {
        id: 'bbb', name: 'tomato', data: [3, 2, 1]
    },
]);

function unpackIntoColumnsAndData(columns) {
    const mockData = { columns: [], data: []};
    columns.forEach(col => {
        col.data.forEach((v, i) => {
            if (!mockData.data[i]) {
                mockData.data[i] = {};
            }
            mockData.data[i][col.id] = v;
        });
        mockData.columns.push(R.dissoc('data', col));
    });
    return mockData;
}

function gendata(func, ndata = N_DATA) {
    return R.range(1, ndata).map(func);
}
