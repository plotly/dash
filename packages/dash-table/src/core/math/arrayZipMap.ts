import * as R from 'ramda';

type Array<T> = T[];

export function arrayMap<T1, TR>(
    a1: Array<T1>,
    cb: (d1: T1, i: number) => TR
) {
    const mapArray = R.addIndex<T1, TR>(R.map);

    return mapArray((iValue, i) => cb(iValue, i), a1);
}

export function arrayMap2<T1, T2, TR>(
    a1: Array<T1>,
    a2: Array<T2>,
    cb: (d1: T1, d2: T2, i: number) => TR
) {
    const mapArray = R.addIndex<T1, TR>(R.map);

    return mapArray((iValue, i) => cb(iValue, a2[i], i), a1);
}

export function arrayMap3<T1, T2, T3, TR>(
    a1: Array<T1>,
    a2: Array<T2>,
    a3: Array<T3>,
    cb: (d1: T1, d2: T2, d3: T3, i: number) => TR
) {
    const mapArray = R.addIndex<T1, TR>(R.map);

    return mapArray((iValue, i) => cb(iValue, a2[i], a3[i], i), a1);

}

export function arrayMapN<TR>(
    cb: (i: number, ...args: any[]) => TR,
    ...arrays: (any[])[]
) {
    const a1 = arrays.slice(0, 1);
    const as = arrays.slice(1);

    const mapArray = R.addIndex<any, TR>(R.map);

    return mapArray((iValue, i) => cb(i, [iValue, ...as.map(a => a[i])]), a1);
}