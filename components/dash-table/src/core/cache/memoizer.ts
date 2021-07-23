import {memoizeOne} from 'core/memoizer';
import {CacheKeyFragment, getCache} from '.';

export default <TKey extends CacheKeyFragment[]>() => {
    return <TEntryFn extends (...a: any[]) => any>(fn: TEntryFn) => {
        const cache = new Map<CacheKeyFragment, any>();

        function get(...key: TKey): TEntryFn {
            const lastKey = key.slice(-1)[0];

            const nestedCache = getCache(cache, ...key);

            return (
                nestedCache.get(lastKey) ||
                nestedCache.set(lastKey, memoizeOne(fn)).get(lastKey)
            );
        }

        return {get};
    };
};
