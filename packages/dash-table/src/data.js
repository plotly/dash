import * as R from 'ramda';
// export const DATA = [
//     {'NYC': 1, 'Paris': 2, 'Montréal': 3},
//     {'NYC': 4, 'Paris': 5, 'Montréal': 6},
//     {'NYC': 7, 'Paris': 8, 'Montréal': 9},
// ]

export const DATA = R.range(1, 5).map(i => ({
    'New York City': i, 'Paris': i*10, 'Montréal': i*100
}));
