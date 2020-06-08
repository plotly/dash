import {
    flatten,
    includes,
    partition,
    pluck,
    sort,
    uniq,
    forEach
} from 'ramda';

import { IStoreState } from '../store';

import {
    aggregateCallbacks,
    removePrioritizedCallbacks,
    addExecutingCallbacks,
    executeCallback
} from '../actions/callbacks';

import { stringifyId } from '../actions/dependencies';

import {
    combineIdAndProp
} from '../actions/dependencies_ts';

import isAppReady from '../actions/isAppReady';

import {
    ICallback,
    IExecutingCallback
} from '../types/callbacks';
import { IStoreObserverDefinition } from '../StoreObserver';

const sortPriority = (c1: ICallback, c2: ICallback): number => {
    return (c1.priority ?? '') > (c2.priority ?? '') ? -1 : 1;
}

const observer: IStoreObserverDefinition<IStoreState> = {
    observer: async ({
        dispatch,
        getState
    }) => {
        const { callbacks: { executing, watched }, config, hooks, layout, paths } = getState();
        let { callbacks: { prioritized } } = getState();

        const available = Math.max(
            0,
            10 - executing.length - watched.length
        );

        // Order prioritized callbacks based on depth and breadth of callback chain
        prioritized = sort(sortPriority, prioritized);

        // Divide between ready and waiting
        const [ready, waiting] = partition(cb => isAppReady(
            layout,
            paths,
            uniq(pluck('id', [
                ...flatten(cb.getInputs(paths)),
                ...flatten(cb.getState(paths))
            ]))
        ) === true, prioritized);

        // Execute sync callbacks
        const readyCallbacks: [ICallback, any][] = ready.map(cb => {
            const { getOutputs } = cb;
            const allOutputs = getOutputs(paths);
            const flatOutputs: any[] = flatten(allOutputs);
            const allPropIds: any[] = [];

            const reqOut: any = {};
            flatOutputs.forEach(({ id, property }) => {
                const idStr = stringifyId(id);
                const idOut = (reqOut[idStr] = reqOut[idStr] || []);
                idOut.push(property);
                allPropIds.push(combineIdAndProp({ id: idStr, property }));
            });
            cb.requestedOutputs = reqOut;

            return [cb, { allOutputs, allPropIds }];
        });

        const syncExecutingCallbacks: IExecutingCallback[] = readyCallbacks.map(([cb, stash]) => {
            return executeCallback(cb, config, hooks, paths, layout, stash);
        });

        dispatch(aggregateCallbacks([
            ready.length ? removePrioritizedCallbacks(ready) : null,
            syncExecutingCallbacks.length ? addExecutingCallbacks(syncExecutingCallbacks) : null
        ]));

        // Execute async callbacks
        const asyncAvailable = available - syncExecutingCallbacks.length;

        prioritized = prioritized.slice(0, asyncAvailable);
        if (!prioritized.length) {
            return;
        }

        forEach(async cb => {
            const { getOutputs } = cb;
            const allOutputs = getOutputs(paths);
            const flatOutputs: any[] = flatten(allOutputs);
            const allPropIds: any[] = [];

            const reqOut: any = {};
            flatOutputs.forEach(({ id, property }) => {
                const idStr = stringifyId(id);
                const idOut = (reqOut[idStr] = reqOut[idStr] || []);
                idOut.push(property);
                allPropIds.push(combineIdAndProp({ id: idStr, property }));
            });
            cb.requestedOutputs = reqOut;

            // Make sure the app is ready to execute callbacks impacting `ids`
            await isAppReady(layout, paths, uniq(pluck('id', [
                ...flatten(cb.getInputs(paths)),
                ...flatten(cb.getState(paths))
            ])));

            // Make
            const { callbacks: { prioritized: updatedPrioritized } } = getState();
            if (!includes(cb, updatedPrioritized)) {
                return;
            }

            const executingCallback = executeCallback(cb, config, hooks, paths, layout, { allOutputs, allPropIds });

            dispatch(aggregateCallbacks([
                removePrioritizedCallbacks([cb]),
                addExecutingCallbacks([executingCallback])
            ]));
        }, waiting);
    },
    inputs: ['callbacks.prioritized', 'callbacks.completed']
};

export default observer;
