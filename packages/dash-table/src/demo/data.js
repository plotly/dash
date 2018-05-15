import * as R from 'ramda';

const N_DATA = 50;

export const mockData = unpackIntoColumnsAndDataFrames([
    {
        id: 'aaa',
        name: ['', 'Weather', 'Temperature'],
        type: 'numeric',
        width: 150,
        data: gendata(i => i + 1),
    },

    {
        id: 'bbb',
        name: ['', 'Weather', 'Climate'],
        // 'type': 'dropdown',
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

    {
        id: 'ccc',
        name: ['City', 'Canada', 'Toronto', ' '],
        type: 'numeric',
        width: 150,
        data: gendata(i => i),
    },

    {
        id: 'ddd',
        name: ['City', 'Canada', 'Montréal'],
        type: 'numeric',
        editable: false,
        width: 150,
        data: gendata(i => i * 100),
    },

    {
        id: 'eee',
        name: ['City', 'America', 'New York City'],
        type: 'numeric',
        style: {
            'white-space': 'pre-line',
        },
        width: 150,
        data: gendata(i => i),
    },

    {
        id: 'fff',
        name: ['City', 'America', 'Boston'],
        type: 'numeric',
        width: 150,
        data: gendata(i => i + 1),
    },

    {
        id: 'ggg',
        name: ['City', 'France', 'Paris'],
        type: 'numeric',
        editable: true,
        width: 150,
        data: gendata(i => i * 10),
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
