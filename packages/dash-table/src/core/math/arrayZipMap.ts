export function arrayMap<T1, TR>(
    a1: T1[],
    fn: (d1: T1, i: number) => TR
): TR[] {
    const _a1_ = a1.length;

    const res: TR[] = new Array<TR>(_a1_);

    for (let i = 0; i < _a1_; ++i) {
        res[i] = fn(a1[i], i);
    }

    return res;
}

export function arrayMap2<T1, T2, TR>(
    a1: T1[],
    a2: T2[],
    fn: (d1: T1, d2: T2, i: number) => TR
): TR[] {
    const _a1_ = a1.length;

    const res: TR[] = new Array<TR>(_a1_);

    for (let i = 0; i < _a1_; ++i) {
        res[i] = fn(a1[i], a2[i], i);
    }

    return res;
}

export function arrayMap3<T1, T2, T3, TR>(
    a1: T1[],
    a2: T2[],
    a3: T3[],
    fn: (d1: T1, d2: T2, d3: T3, i: number) => TR
): TR[] {
    const _a1_ = a1.length;

    const res: TR[] = new Array<TR>(_a1_);

    for (let i = 0; i < _a1_; ++i) {
        res[i] = fn(a1[i], a2[i], a3[i], i);
    }

    return res;
}

export function arrayMapN<TR>(
    fn: (i: number, ...args: any[]) => TR,
    ...arrays: any[][]
) {
    const a1 = arrays.slice(0, 1);
    const as = arrays.slice(1);

    const _a1_ = a1.length;

    const res: TR[] = new Array<TR>(_a1_);

    for (let i = 0; i < _a1_; ++i) {
        res[i] = fn(i, a1[i], ...as.map(a => a[i]));
    }

    return res;
}
