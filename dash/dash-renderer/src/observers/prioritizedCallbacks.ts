import {find, flatten, map, partition, pluck, sort, uniq} from 'ramda';

import {IStoreState} from '../store';

import {
    addBlockedCallbacks,
    addExecutingCallbacks,
    aggregateCallbacks,
    executeCallback,
    removeBlockedCallbacks,
    removePrioritizedCallbacks
} from '../actions/callbacks';

import {stringifyId} from '../actions/dependencies';

import {combineIdAndProp} from '../actions/dependencies_ts';

import isAppReady from '../actions/isAppReady';

import {
    IBlockedCallback,
    ICallback,
    IExecutingCallback,
    ILayoutCallbackProperty,
    IPrioritizedCallback
} from '../types/callbacks';
import {IStoreObserverDefinition} from '../StoreObserver';
import {getAppState} from '../reducers/constants';

const sortPriority = (c1: ICallback, c2: ICallback): number => {
    return (c1.priority ?? '') > (c2.priority ?? '') ? -1 : 1;
};

const getStash = (
    cb: IPrioritizedCallback,
    paths: any
): {
    allOutputs: ILayoutCallbackProperty[][];
    allPropIds: any[];
} => {
    const {getOutputs} = cb;
    const allOutputs = getOutputs(paths);
    const flatOutputs: any[] = flatten(allOutputs);
    const allPropIds: any[] = [];

    const reqOut: any = {};
    flatOutputs.forEach(({id, property}) => {
        const idStr = stringifyId(id);
        const idOut = (reqOut[idStr] = reqOut[idStr] || []);
        idOut.push(property);
        allPropIds.push(combineIdAndProp({id: idStr, property}));
    });

    return {allOutputs, allPropIds};
};

const getIds = (cb: ICallback, paths: any) =>
    uniq(
        pluck('id', [
            ...flatten(cb.getInputs(paths)),
            ...flatten(cb.getState(paths))
        ])
    );

const observer: IStoreObserverDefinition<IStoreState> = {
    observer: async ({dispatch, getState}) => {
        const {
            callbacks: {executing, watched},
            config,
            hooks,
            layout,
            paths,
            appLifecycle
        } = getState();
        let {
            callbacks: {prioritized}
        } = getState();

        if (appLifecycle !== getAppState('HYDRATED')) {
            return;
        }

        const available = Math.max(0, 12 - executing.length - watched.length);

        // Order prioritized callbacks based on depth and breadth of callback chain
        prioritized = sort(sortPriority, prioritized);

        // Divide between sync and async
        const [syncCallbacks, asyncCallbacks] = partition(
            cb => isAppReady(layout, paths, getIds(cb, paths)) === true,
            prioritized
        );

        const pickedSyncCallbacks = syncCallbacks.slice(0, available);
        const pickedAsyncCallbacks = asyncCallbacks.slice(
            0,
            available - pickedSyncCallbacks.length
        );

        if (pickedSyncCallbacks.length) {
            const executingCallbacks: IExecutingCallback[] = [];
            for (let index = 0; index < pickedSyncCallbacks.length; index++) {
                const element = pickedSyncCallbacks[index];
                executingCallbacks.push(
                    await executeCallback(
                        element,
                        config,
                        hooks,
                        paths,
                        layout,
                        getStash(element, paths),
                        dispatch
                    )
                );
            }

            dispatch(
                aggregateCallbacks([
                    removePrioritizedCallbacks(pickedSyncCallbacks),
                    addExecutingCallbacks(executingCallbacks)
                ])
            );
        }

        if (pickedAsyncCallbacks.length) {
            const deferred = map<IPrioritizedCallback, IBlockedCallback>(
                cb => ({
                    ...cb,
                    ...getStash(cb, paths),
                    isReady: isAppReady(layout, paths, getIds(cb, paths))
                }),
                pickedAsyncCallbacks
            );

            dispatch(
                aggregateCallbacks([
                    removePrioritizedCallbacks(pickedAsyncCallbacks),
                    addBlockedCallbacks(deferred)
                ])
            );
            for (const i in deferred) {
                const cb = deferred[i];
                await cb.isReady;

                const {
                    callbacks: {blocked}
                } = getState();

                // Check if it's been removed from the `blocked` list since - on
                // callback completion, another callback may be cancelled
                // Find the callback instance or one that matches its promise
                // (eg. could have been pruned)
                const currentCb = find(
                    _cb => _cb === cb || _cb.isReady === cb.isReady,
                    blocked
                );
                if (!currentCb) {
                    return;
                }

                const executingCallback = await executeCallback(
                    cb,
                    config,
                    hooks,
                    paths,
                    layout,
                    cb,
                    dispatch
                );
                dispatch(
                    aggregateCallbacks([
                        removeBlockedCallbacks([cb]),
                        addExecutingCallbacks([executingCallback])
                    ])
                );
            }
            // forEach(async cb => {

            // }, deferred);
        }
    },
    inputs: ['callbacks.prioritized', 'callbacks.completed']
};

export default observer;
