export default (
    i: number,
    last: number,
    flag?: boolean | boolean[] | 'first' | 'last'
): boolean =>
    flag === 'last'
        ? i === last
        : flag === 'first'
        ? i === 0
        : typeof flag === 'boolean'
        ? flag
        : !!flag && flag[i];
