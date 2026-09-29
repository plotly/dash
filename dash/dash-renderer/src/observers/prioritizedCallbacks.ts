import {find, flatten, map, partition, sort} from 'ramda';

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

import {MAX_CONCURRENT_HTTP_CALLBACKS, usesRequestSlot} from './requestSlot';

import {
    IBlockedCallback,
    ICallback,
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

const getIds = (cb: ICallback, paths: any) => {
    const items = [
        ...flatten(cb.getInputs(paths)),
        ...flatten(cb.getState(paths))
    ];

    const uniqueIds = new Map(items.map(item => [stringifyId(item.id), item]));
    const uniqueItems = Array.from(uniqueIds.values());
    return uniqueItems;
};

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

        // Only callbacks holding an in-flight HTTP request count toward the
        // budget; clientside, streaming and websocket-routed ones are exempt.
        const countsToward = (cb: ICallback) => usesRequestSlot(cb, config);

        const inFlight =
            executing.filter(countsToward).length +
            watched.filter(countsToward).length;
        const available = Math.max(0, MAX_CONCURRENT_HTTP_CALLBACKS - inFlight);

        // Order prioritized callbacks based on depth and breadth of callback chain
        prioritized = sort(sortPriority, prioritized);

        // Exempt callbacks always dispatch; only request-slot callbacks are
        // limited to the available budget (ready ones first, as before).
        const [budgeted, exempt] = partition(countsToward, prioritized);

        const isReady = (cb: ICallback) =>
            isAppReady(layout, paths, getIds(cb, paths)) === true;

        const [budgetedSync, budgetedAsync] = partition(isReady, budgeted);
        const pickedBudgetedSync = budgetedSync.slice(0, available);
        const pickedBudgetedAsync = budgetedAsync.slice(
            0,
            available - pickedBudgetedSync.length
        );

        const [exemptSync, exemptAsync] = partition(isReady, exempt);

        // Divide between sync (components ready) and async (deferred until ready)
        const pickedSyncCallbacks = [...exemptSync, ...pickedBudgetedSync];
        const pickedAsyncCallbacks = [...exemptAsync, ...pickedBudgetedAsync];

        if (pickedSyncCallbacks.length) {
            dispatch(
                aggregateCallbacks([
                    removePrioritizedCallbacks(pickedSyncCallbacks),
                    addExecutingCallbacks(
                        map(
                            cb =>
                                executeCallback(
                                    cb,
                                    config,
                                    hooks,
                                    paths,
                                    layout,
                                    getStash(cb, paths),
                                    dispatch,
                                    getState
                                ),
                            pickedSyncCallbacks
                        )
                    )
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

            deferred.forEach(async cb => {
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

                const executingCallback = executeCallback(
                    cb,
                    config,
                    hooks,
                    paths,
                    layout,
                    cb,
                    dispatch,
                    getState
                );

                dispatch(
                    aggregateCallbacks([
                        removeBlockedCallbacks([cb]),
                        addExecutingCallbacks([executingCallback])
                    ])
                );
            });
        }
    },
    inputs: ['callbacks.prioritized', 'callbacks.completed']
};

export default observer;
