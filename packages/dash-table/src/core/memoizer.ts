import {isEqualArgs} from 'core/comparer';
import {ResultFn} from 'core/generic';

interface ICachedResultFn<TEntry> {
    result: TEntry;
    cached: boolean;
    first: boolean;
}

export function memoizeOne<TArgs extends any[], TEntry>(
    fn: ResultFn<TArgs, TEntry>
): ResultFn<TArgs, TEntry> {
    let lastArgs: any[] | null = null;
    let lastResult: any;

    return (...args: TArgs): TEntry =>
        isEqualArgs(lastArgs, args)
            ? lastResult
            : (lastArgs = args) && (lastResult = fn(...args));
}

export function memoizeOneFactory<TArgs extends any[], TEntry>(
    fn: ResultFn<TArgs, TEntry>
): () => ResultFn<TArgs, TEntry> {
    return () => memoizeOne(fn);
}

export function memoizeOneWithFlag<TArgs extends any[], TEntry>(
    fn: ResultFn<TArgs, TEntry>
): ResultFn<TArgs, ICachedResultFn<TEntry>> {
    let lastArgs: any[] | null = null;
    let lastResult: any;
    let isFirst = true;

    return (...args: TArgs): ICachedResultFn<TEntry> => {
        const res = isEqualArgs(lastArgs, args)
            ? {cached: true, first: isFirst, result: lastResult}
            : {
                  cached: false,
                  first: isFirst,
                  result: (lastArgs = args) && (lastResult = fn(...args))
              };
        isFirst = false;

        return res;
    };
}

export function memoizeAll<TArgs extends any[], TEntry>(
    fn: ResultFn<TArgs, TEntry>
): ResultFn<TArgs, TEntry> {
    const cache: {args: TArgs; result: TEntry}[] = [];

    return (...args: TArgs): TEntry => {
        const entry = cache.find(e => isEqualArgs(e.args, args));

        return (entry || cache[cache.push({args, result: fn(...args)}) - 1])
            .result;
    };
}
