import * as R from 'ramda';

export type CacheKeyFragment = string | number | boolean;

export function getCache<TKey extends CacheKeyFragment[]>(
    cache: Map<CacheKeyFragment, any>,
    ...key: TKey
) {
    const cacheKeys = key.slice(0, -1);

    return R.reduce(
        (c, fragment) => {
            return c.get(fragment) || c.set(fragment, new Map()).get(fragment);
        },
        cache,
        cacheKeys
    ) as Map<CacheKeyFragment, any>;
}
