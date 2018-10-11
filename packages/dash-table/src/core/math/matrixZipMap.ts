import * as R from 'ramda';

type Matrix<T> = T[][];

export function matrixMap<T1, T2, TR>(
    m1: Matrix<T1>,
    m2: Matrix<T2>,
    cb: (d1: T1, d2: T2, i: number, j: number) => TR
) {
    const mapMatrix = R.addIndex<T1[], TR[]>(R.map);
    const mapRow = R.addIndex<T1, TR>(R.map);

    return mapMatrix((iRow, i) =>
        mapRow(
            (ijValue, j) => cb(ijValue, m2[i][j], i, j),
            iRow
        ), m1
    );
}

export function matrixMap3<T1, T2, T3, TR>(
    m1: Matrix<T1>,
    m2: Matrix<T2>,
    m3: Matrix<T3>,
    cb: (d1: T1, d2: T2, d3: T3, i: number, j: number) => TR
) {
    const mapMatrix = R.addIndex<T1[], TR[]>(R.map);
    const mapRow = R.addIndex<T1, TR>(R.map);

    return mapMatrix((iRow, i) =>
        mapRow(
            (ijValue, j) => cb(ijValue, m2[i][j], m3[i][j], i, j),
            iRow
        ), m1
    );
}

export function matrixMap4<T1, T2, T3, T4, TR>(
    m1: Matrix<T1>,
    m2: Matrix<T2>,
    m3: Matrix<T3>,
    m4: Matrix<T4>,
    cb: (d1: T1, d2: T2, d3: T3, d4: T4, i: number, j: number) => TR
) {
    const mapMatrix = R.addIndex<T1[], TR[]>(R.map);
    const mapRow = R.addIndex<T1, TR>(R.map);

    return mapMatrix((iRow, i) =>
        mapRow(
            (ijValue, j) => cb(ijValue, m2[i][j], m3[i][j], m4[i][j], i, j),
            iRow
        ), m1
    );
}

export function matrixMapN<TR>(
    cb: (i: number, j: number, ...args: any[]) => TR,
    ...matrices: (any[][])[]
) {
    const m1 = matrices.slice(0, 1);
    const ms = matrices.slice(1);

    const mapMatrix = R.addIndex<any[], TR[]>(R.map);
    const mapRow = R.addIndex<any, TR>(R.map);

    return mapMatrix((iRow, i) =>
        mapRow(
            (ijValue, j) => cb(i, j, [ijValue, ...ms.map(m => m[i][j])]),
            iRow
        ), m1
    );
}