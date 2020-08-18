import { lazy } from 'react';

export const asyncDecorator = (target, promise, overrideProps = false) => {
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

                if (overrideProps) {
                    const source = res.default;

                    target.defaultProps = source.defaultProps;
                    target.propTypes = source.propTypes;
                    listeners.forEach(listener => listener());
                }

                return res;
            });
        }),
    };

    Object.defineProperty(target, '_dashprivate_isLazyComponentReady', {
        get: () => state.isReady
    });

    Object.defineProperty(target, '_dashprivate_overrideProps', {
        get: () => overrideProps
    });

    const listeners = [];
    if (overrideProps) {
        Object.defineProperty(target, '_dashprivate_onOverrideProps', {
            get: () => fn => {
                listeners.push(fn);

                return () => listeners.splice(
                    listeners.findIndex(listener => listener === fn),
                    1
                );
            }
        });
    }

    return state.get;
};

export const inheritAsyncDecorator = (target, source) => {
    Object.defineProperty(target, '_dashprivate_isLazyComponentReady', {
        get: () => isReady(source)
    });
}

export const isReady = target => target?._dashprivate_isLazyComponentReady;

export const overridesProps = target => target?._dashprivate_overrideProps;

export const onOverrideProps = (target, fn) => target?._dashprivate_onOverrideProps?.(fn);
