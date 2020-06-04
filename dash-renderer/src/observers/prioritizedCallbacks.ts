import {
    flatten,
    includes,
    map,
    partition,
    pluck,
    reduce,
    sort,
    uniq
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
    IExecutingCallback,
    ICallbackProperty
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

        prioritized = prioritized.slice(0, available);
        if (!prioritized.length) {
            return;
        }

        const callbacks: [ICallback, any][] = prioritized.map(cb => {
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

        const ids = reduce((res, [cb]) => ([
            ...res,
            ...flatten(cb.getInputs(paths)),
            ...flatten(cb.getState(paths))
        ]), [] as ICallbackProperty[], callbacks);

        /*
            Make sure the app is ready to execute callbacks impacting `ids`
        */
        await isAppReady(layout, paths, uniq(pluck('id', ids)));

        /*
            Make sure to only execute callbacks that are still in the `prioritized` list (isAppReady is async - state could have changed)
        */
        const { callbacks: { prioritized: updatedPrioritized } } = getState();
        const [remainingCallbacks] = partition(
            ([cb]) => includes(cb, updatedPrioritized),
            callbacks
        );

        const executingCallbacks: IExecutingCallback[] = remainingCallbacks.map(([cb, stash]) => {
            return executeCallback(cb, config, hooks, paths, layout, stash);
        });

        dispatch(aggregateCallbacks([
            remainingCallbacks.length ? removePrioritizedCallbacks(map(([cb]) => cb, remainingCallbacks)) : null,
            executingCallbacks.length ? addExecutingCallbacks(executingCallbacks) : null
        ]));

    },
    inputs: ['callbacks.prioritized', 'callbacks.completed']
};

export default observer;
