import { lazy } from 'react';

export const decorate = (target, promise) => {
    let resolve;
    const isReady = new Promise(r => {
        resolve = r;
    });

    const state = {
        isReady,
        get: lazy(() => {
            return Promise.resolve(promise()).then(res => {
                setTimeout(async () => {
                    await resolve(true);
                    state.isReady = true;
                }, 0);

                return res;
            });
        }),
    };

    Object.defineProperty(target, '_dashprivate_isLazyComponentReady', {
        get: () => state.isReady,
    });

    return state.get;
};

export const isReady = target => target &&
    target._dashprivate_isLazyComponentReady;
