import { lazy } from 'react';

const isLazyProp = '_dashprivate_isLazyComponentReady';

export const asyncDecorator = (target, promise) => {
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

    Object.defineProperty(target, isLazyProp, {
        get: () => state.isReady
    });

    return state.get;
};

export const setDecorator = (target, source) => {
    Object.defineProperty(target, isLazyProp, {
        get: () => isReady(source)
    });
}

export const isReady = target => target &&
    target._dashprivate_isLazyComponentReady;
