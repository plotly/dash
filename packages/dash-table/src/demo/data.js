import * as R from 'ramda';
// export const DATA = [
//     {'New York City': 1, 'Paris': 2, 'Montréal': 3},
//     {'New York City': 4, 'Paris': 5, 'Montréal': 6},
//     {'New York City': 7, 'Paris': 8, 'Montréal': 9},
// ]


export const DATA = R.range(1, 5).map(i => ({
    ' ': i,
    'New York City': i,
    'Paris': i*10,
    'Montréal': i*100,
    'Climate': 'Tropical Beaches'
}));

// export const DATA = [
//     {'New York City': 1, 'Paris': 3, 'Montréal': 1, ' ': 1},
//     {'New York City': 1, 'Paris': 2, 'Montréal': 2, ' ': 2},
//     {'New York City': 1, 'Paris': 1, 'Montréal': 3, ' ': 3},
//
//     {'New York City': 2, 'Paris': 3, 'Montréal': 4, ' ': 4},
//     {'New York City': 2, 'Paris': 2, 'Montréal': 5, ' ': 5},
//     {'New York City': 2, 'Paris': 1, 'Montréal': 6, ' ': 6},
// ];

// export const DATA = R.range(1, 7).map(i => ({
//     ' ': i,
//     'New York City': [1, 1, 1, 2, 2, 2],
//     'Paris': [3, 2, 1, 3, 2, 1],
//     'Montréal': i*100
// }));
