import {
    all,
    concat,
    difference,
    filter,
    flatten,
    groupBy,
    intersection,
    isEmpty,
    isNil,
    map,
    values
} from 'ramda';

import { IStoreState } from "../store";

import {
    aggregateCallbacks,
    removeRequestedCallbacks,
    removePrioritizedCallbacks,
    removeExecutingCallbacks,
    removeWatchedCallbacks,
    addRequestedCallbacks,
    addPrioritizedCallbacks,
    addExecutingCallbacks,
    addWatchedCallbacks
} from '../actions/callbacks';

import { isMultiValued } from '../actions/dependencies';

import {
    combineIdAndProp,
    getReadyCallbacks,
    getUniqueIdentifier,
    pruneCallbacks
} from '../actions/dependencies_ts';

import {
    ICallback,
    IExecutingCallback,
    IStoredCallback
} from '../types/callbacks';

import { getPendingCallbacks } from "../utils/callbacks";
import { IStoreObserverDefinition } from '../StoreObserver';

const observer: IStoreObserverDefinition<IStoreState> = {
    observer: ({
        dispatch,
        getState
    }) => {
        const { callbacks, callbacks: { prioritized, executing, watched, executed, completed, stored }, paths } = getState();
        let { callbacks: { requested } } = getState();

        const pendingCallbacks = getPendingCallbacks(callbacks);

        console.log('onCallbacksChanged.requested', requested, completed, callbacks);

        /*
            1. Remove duplicated `requested` callbacks
        */

        /*
            Extract all but the first callback from each IOS-key group
            these callbacks are duplicates.
        */
        const rDuplicates = flatten(map(
            group => group.slice(0, -1),
            // group => filter(cb => !cb.executionGroup, group).slice(1),
            values(
                groupBy<ICallback>(
                    getUniqueIdentifier,
                    requested
                )
            )
        ));

        /*
            TODO?
            Clean up the `requested` list - during the dispatch phase,
            duplicates will be removed for real
        */
        requested = difference(requested, rDuplicates);

        /*
            2. Remove duplicated `prioritized`, `executing` and `watching` callbacks
        */

        /*
            Extract all but the first callback from each IOS-key group
            these callbacks are `prioritized` and duplicates.
        */
        const pDuplicates = flatten(map(
            group => group.slice(0, -1),
            // group => filter(cb => !cb.executionGroup, group).slice(1),
            values(
                groupBy<ICallback>(
                    getUniqueIdentifier,
                    concat(prioritized, requested)
                )
            )
        ));

        const eDuplicates = flatten(map(
            group => group.slice(0, -1),
            // group => filter(cb => !cb.executionGroup, group).slice(1),
            values(
                groupBy<ICallback>(
                    getUniqueIdentifier,
                    concat(executing, requested)
                )
            )
        )) as IExecutingCallback[];

        const wDuplicates = flatten(map(
            group => group.slice(0, -1),
            // group => filter(cb => !cb.executionGroup, group).slice(1),
            values(
                groupBy<ICallback>(
                    getUniqueIdentifier,
                    concat(watched, requested)
                )
            )
        )) as IExecutingCallback[];

        if (rDuplicates.length || pDuplicates.length || eDuplicates.length || wDuplicates.length) {
            console.log('onCallbacksChanged.requested', '[duplicates]', rDuplicates.length, pDuplicates.length, eDuplicates.length, wDuplicates.length);
        }

        /*
            3. Modify or remove callbacks that are outputing to non-existing layout `id`.
        */

        const { added: rAdded, removed: rRemoved } = pruneCallbacks(requested, paths);
        const { added: pAdded, removed: pRemoved } = pruneCallbacks(prioritized, paths);
        const { added: eAdded, removed: eRemoved } = pruneCallbacks(executing, paths);
        const { added: wAdded, removed: wRemoved } = pruneCallbacks(watched, paths);

        if (rRemoved.length + pRemoved.length + eRemoved.length + wRemoved.length) {
            console.log('onCallbacksChanged.requested', '[pruned]', rRemoved.length, pRemoved.length, eRemoved.length, wRemoved.length);
        }

        /*
            TODO?
            Clean up the `requested` list - during the dispatch phase,
            it will be updated for real
        */
        requested = concat(
            difference(
                requested,
                rRemoved
            ),
            rAdded
        );

        /*
            4. Find `requested` callbacks that do not depend on a outstanding output (as either input or state)
        */
        let readyCallbacks = getReadyCallbacks(requested, pendingCallbacks);
        console.log('onCallbacksChanged.requested', '[readyCallbacks]', readyCallbacks);

        /*
            If:
            - there are `requested` callbacks
            - no `requested` callback can be promoted to `prioritized`
            - no callbacks are `prioritized`, `executing`, `watched` or `executed`
            Then:
            - the `requested` callbacks form a ciruclar dependency and can never be executed
            - prune them out of `requested`
        */
        const rCircular = (
            !readyCallbacks.length &&
            !prioritized.length &&
            !executing.length &&
            !watched.length &&
            !executed.length &&
            requested.length
        ) ? requested : [];

        /*
            5. Prune callbacks that became irrelevant in their `executionGroup`
        */
        const pendingGroups = groupBy<IStoredCallback>(
            cb => cb.executionGroup as any,
            filter(cb => !isNil(cb.executionGroup), stored)
        );
        console.log('onCallbacksChanged.requested', '[pendingGroups]', pendingGroups, map(pg => flatten(map(
            gcb => gcb.executionMeta.updatedProps,
            pg
        )), values(pendingGroups)));

        const dropped: ICallback[] = filter(cb => {
            if (!cb.executionGroup || !pendingGroups[cb.executionGroup] || !pendingGroups[cb.executionGroup].length) {
                return false;
            }

            const inputs = map(combineIdAndProp, flatten(cb.getInputs(paths)));

            const allProps = flatten(map(
                gcb => gcb.executionMeta.allProps,
                pendingGroups[cb.executionGroup]
            ));

            const updated = flatten(map(
                gcb => gcb.executionMeta.updatedProps,
                pendingGroups[cb.executionGroup]
            ));

            const res =
                isEmpty(intersection(
                    inputs,
                    updated
                )) &&
                isEmpty(difference(
                    inputs,
                    allProps
                ))
                && !all(
                    isMultiValued,
                    cb.callback.inputs
                );

            console.log('SPECIAL', cb, res, inputs, allProps, updated);

            return res;
        },
            readyCallbacks
        );

        console.log('onCallbacksChanged.requested', '[dropped]', readyCallbacks, dropped, pendingGroups);

        /*
            TODO?
            Clean up the `requested` list - during the dispatch phase,
            it will be updated for real
        */
        requested = difference(
            requested,
            dropped
        );

        readyCallbacks = difference(
            readyCallbacks,
            dropped
        );

        dispatch(aggregateCallbacks([
            // Clean up duplicated callbacks
            rDuplicates.length ? removeRequestedCallbacks(rDuplicates) : null,
            pDuplicates.length ? removePrioritizedCallbacks(pDuplicates) : null,
            eDuplicates.length ? removeExecutingCallbacks(eDuplicates) : null,
            wDuplicates.length ? removeWatchedCallbacks(wDuplicates) : null,
            // Prune callbacks
            rRemoved.length ? removeRequestedCallbacks(rRemoved) : null,
            rAdded.length ? addRequestedCallbacks(rAdded) : null,
            pRemoved.length ? removePrioritizedCallbacks(pRemoved) : null,
            pAdded.length ? addPrioritizedCallbacks(pAdded) : null,
            eRemoved.length ? removeExecutingCallbacks(eRemoved) : null,
            eAdded.length ? addExecutingCallbacks(eAdded) : null,
            wRemoved.length ? removeWatchedCallbacks(wRemoved) : null,
            wAdded.length ? addWatchedCallbacks(wAdded) : null,
            // Prune circular callbacks
            rCircular.length ? removeRequestedCallbacks(rCircular) : null,
            // Drop non-triggered initial callbacks
            dropped.length ? removeRequestedCallbacks(dropped) : null,
            // Promote callbacks
            readyCallbacks.length ? removeRequestedCallbacks(readyCallbacks) : null,
            readyCallbacks.length ? addPrioritizedCallbacks(readyCallbacks) : null
        ]));
    },
    inputs: ['callbacks.requested', 'callbacks.completed']
};

export default observer;