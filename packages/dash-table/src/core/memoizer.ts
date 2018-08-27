import { isEqualArgs } from 'core/comparer';

type ResultFn<TArgs extends any[], TEntry> = (...args: TArgs) => TEntry;

export function memoizeOne<
    TArgs extends any[],
    TEntry
    >(fn: ResultFn<TArgs, TEntry>): ResultFn<TArgs, TEntry> {
    let lastArgs: any[] | null = null;
    let lastResult: any;

    return (...args: TArgs): TEntry => {
        return isEqualArgs(lastArgs, args) ?
            lastResult :
            (lastArgs = args) && (lastResult = fn(...args));
    };
}

export function memoizeAll<
    TArgs extends any[],
    TEntry
    >(fn: ResultFn<TArgs, TEntry>): ResultFn<TArgs, TEntry> {
    const cache: { args: TArgs, result: TEntry }[] = [];

    return (...args: TArgs): TEntry => {
        let entry = cache.find(e => isEqualArgs(e.args, args));

        return (
            entry ||
            cache[cache.push({ args, result: fn(...args) }) - 1]
        ).result;
    };
}