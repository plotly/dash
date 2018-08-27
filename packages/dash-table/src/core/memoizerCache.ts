import * as R from 'ramda';
import { memoizeOne } from 'core/memoizer';

type CacheKeyFragment = string | number | boolean;

function memoize<TArgs extends any[], TEntry>(fn: (...args: TArgs) => TEntry) {
    return memoizeOne((...args: TArgs) => fn(...args));
}

export default function memoizerCache<
    TKey extends CacheKeyFragment[],
    TArgs extends any[],
    TEntry
    >(fn: (...args: TArgs) => TEntry)
{
    const cache = new Map<CacheKeyFragment, any>();

    return (key: TKey, args: TArgs): TEntry => {
        const lastKey = key.slice(-1)[0];
        const cacheKeys = key.slice(0, -1);

        const fnCacne = R.reduce((c, fragment) => {
            return c.get(fragment) || c.set(fragment, new Map()).get(fragment);
        }, cache, cacheKeys);

        return (
            fnCacne.get(lastKey) ||
            fnCacne.set(lastKey, memoize<TArgs, TEntry>(fn)).get(lastKey)
        )(...args);
    };
}