import {
    partition,
    assoc,
    find
} from 'ramda';

import {
    aggregateCallbacks,
    removeExecutingCallbacks,
    removeWatchedCallbacks,
    addWatchedCallbacks,
    addExecutedCallbacks
} from '../actions/callbacks';

import {
    IExecutingCallback,
} from '../types/callbacks';
import { IStoreObserverDefinition } from '../StoreObserver';
import { IStoreState } from '../store';

const observer: IStoreObserverDefinition<IStoreState> = {
    observer: ({
        dispatch,
        getState
    }) => {
        const {
            callbacks: {
                executing
            },
        } = getState();

        const [deferred, skippedOrReady] = partition(cb => cb.executionPromise instanceof Promise, executing);

        dispatch(aggregateCallbacks([
            executing.length ? removeExecutingCallbacks(executing) : null,
            deferred.length ? addWatchedCallbacks(deferred) : null,
            skippedOrReady.length ? addExecutedCallbacks(skippedOrReady.map(cb => assoc('executionResult', cb.executionPromise as any, cb))) : null
        ]));

        deferred.forEach(async function (cb: IExecutingCallback) {
            const result = await cb.executionPromise;

            // Check if it's been removed from the `watched` list since - on callback completion, another callback may be cancelled
            const { callbacks: { watched } } = getState();

            // Find the callback instance or one that matches its promise (eg. could have been pruned)
            const currentCb = find(_cb => _cb === cb || _cb.executionPromise === cb.executionPromise, watched);
            if (!currentCb) {
                return;
            }

            // Otherwise move to `executed` and remove from `watched`
            dispatch(aggregateCallbacks([
                removeWatchedCallbacks([currentCb]),
                addExecutedCallbacks([{
                    ...currentCb,
                    executionResult: result
                }])
            ]));
        });
    },
    inputs: ['callbacks.executing']
};

export default observer;
