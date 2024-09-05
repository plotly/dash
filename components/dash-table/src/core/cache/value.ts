import {CacheKeyFragment, getCache} from '.';

export default <TKey extends CacheKeyFragment[]>() =>
    <TEntry>(fn: (...a: TKey) => TEntry) => {
        const cache = new Map<CacheKeyFragment, any>();

        function get(...key: TKey): TEntry {
            const lastKey = key.slice(-1)[0];

            const nestedCache = getCache(cache, ...key);

            return nestedCache.has(lastKey)
                ? nestedCache.get(lastKey)
                : nestedCache.set(lastKey, fn(...key)).get(lastKey);
        }

        return {get};
    };
