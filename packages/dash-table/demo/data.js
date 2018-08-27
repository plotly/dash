/* eslint no-magic-numbers: 0 */
import * as R from 'ramda';

const N_DATA = 5000;

export const mockData = unpackIntoColumnsAndDataFrames([
    {
        id: 'rows',
        type: 'numeric',
        width: 40,
        editable: false,
        data: gendata(i => i)
    },

    {
        id: 'ccc',
        name: ['City', 'Canada', 'Toronto'],
        type: 'numeric',
        width: 150,
        data: gendata(i => i),
    },

    {
        id: 'ddd',
        name: ['City', 'Canada', 'Montréal'],
        type: 'numeric',
        width: 150,
        data: gendata(i => i * 100),
    },

    {
        id: 'eee',
        name: ['City', 'America', 'New York City'],
        type: 'numeric',
        width: 150,
        data: gendata(i => i),
    },

    {
        id: 'fff',
        name: ['City', 'America', 'Boston'],
        type: 'numeric',
        width: 150,
        data: gendata(i => i + 1)
    },

    {
        id: 'ggg',
        name: ['City', 'France', 'Paris'],
        type: 'numeric',
        editable: true,
        width: 150,
        data: gendata(i => i * 10),
    },

    {
        id: 'bbb',
        name: ['', 'Weather', 'Climate'],
        type: 'dropdown',
        clearable: true,
        width: 200,
        data: gendata(
            i => ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'][i % 4]
        )
    },

    {
        id: 'aaa',
        name: ['', 'Weather', 'Temperature'],
        type: 'numeric',
        width: 150,
        data: gendata(i => i + 1),
    }
]);

export const mockDataSimple = unpackIntoColumnsAndDataFrames([
    {
        id: 'aaa',
        name: 'Temperature',
        type: 'numeric',
        width: 150,
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
        width: 200,
        data: gendata(
            i => ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'][i % 4]
        ),
    },
]);

export const miniData = unpackIntoColumnsAndDataFrames([
    {
        id: 'aaa', name: 'cheese', data: [1, 2, 3]
    },
    {
        id: 'bbb', name: 'tomato', data: [3, 2, 1]
    },
]);

function unpackIntoColumnsAndDataFrames(columns) {
    const mockData = {columns: [], dataframe: []};
    columns.forEach(col => {
        col.data.forEach((v, i) => {
            if (!mockData.dataframe[i]) {
                mockData.dataframe[i] = {};
            }
            mockData.dataframe[i][col.id] = v;
        });
        mockData.columns.push(R.dissoc('data', col));
    });
    return mockData;
}

function gendata(func, ndata = N_DATA) {
    return R.range(1, ndata).map(func);
}
