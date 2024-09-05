import {
    all,
    concat,
    difference,
    filter,
    flatten,
    groupBy,
    includes,
    intersection,
    isEmpty,
    isNil,
    map,
    mergeLeft,
    mergeWith,
    pluck,
    reduce,
    values
} from 'ramda';

import {IStoreState} from '../store';

import {
    aggregateCallbacks,
    removePrioritizedCallbacks,
    removeExecutingCallbacks,
    removeWatchedCallbacks,
    addPrioritizedCallbacks,
    addExecutingCallbacks,
    addWatchedCallbacks,
    removeBlockedCallbacks,
    addBlockedCallbacks,
    addRequestedCallbacks,
    removeRequestedCallbacks
} from '../actions/callbacks';

import {isMultiValued} from '../actions/dependencies';

import {
    combineIdAndProp,
    getReadyCallbacks,
    getUniqueIdentifier,
    pruneCallbacks
} from '../actions/dependencies_ts';

import {
    ICallback,
    IExecutingCallback,
    IStoredCallback,
    IBlockedCallback
} from '../types/callbacks';

import wait from './../utils/wait';

import {getPendingCallbacks} from '../utils/callbacks';
import {IStoreObserverDefinition} from '../StoreObserver';

const observer: IStoreObserverDefinition<IStoreState> = {
    observer: async ({dispatch, getState}) => {
        await wait(0);

        const {
            callbacks,
            callbacks: {prioritized, blocked, executing, watched, stored},
            paths,
            graphs
        } = getState();
        let {
            callbacks: {requested}
        } = getState();

        const initialRequested = requested.slice(0);

        const pendingCallbacks = getPendingCallbacks(callbacks);

        /*
            0. Prune circular callbacks that have completed the loop
            - cb.callback included in cb.predecessors
        */
        const rCirculars = filter(
            cb => includes(cb.callback, cb.predecessors ?? []),
            requested
        );

        /*
            TODO?
            Clean up the `requested` list - during the dispatch phase,
            circulars will be removed for real
        */
        requested = difference(requested, rCirculars);

        /*
            1. Remove duplicated `requested` callbacks - give precedence to newer callbacks over older ones
        */

        let rDuplicates: ICallback[] = [];
        const rMergedDuplicates: ICallback[] = [];

        values(groupBy<ICallback>(getUniqueIdentifier, requested)).forEach(
            group => {
                if (group.length === 1) {
                    // keep callback if its the only one of its kind
                    rMergedDuplicates.push(group[0]);
                } else {
                    const initial = group.find(cb => cb.initialCall);
                    if (initial) {
                        // drop the initial callback if it's not alone
                        rDuplicates.push(initial);
                    }

                    const groupWithoutInitial = group.filter(
                        cb => cb !== initial
                    );
                    if (groupWithoutInitial.length === 1) {
                        // if there's only one callback beside the initial one, keep that callback
                        rMergedDuplicates.push(groupWithoutInitial[0]);
                    } else {
                        // otherwise merge all remaining callbacks together
                        rDuplicates = concat(rDuplicates, groupWithoutInitial);
                        rMergedDuplicates.push(
                            mergeLeft(
                                {
                                    changedPropIds: reduce(
                                        mergeWith(Math.max),
                                        {},
                                        pluck(
                                            'changedPropIds',
                                            groupWithoutInitial
                                        )
                                    ),
                                    executionGroup: filter(
                                        exg => Boolean(exg),
                                        pluck(
                                            'executionGroup',
                                            groupWithoutInitial
                                        )
                                    ).slice(-1)[0]
                                } as any,
                                groupWithoutInitial.slice(-1)[0]
                            ) as ICallback
                        );
                    }
                }
            }
        );

        /*
            TODO?
            Clean up the `requested` list - during the dispatch phase,
            duplicates will be removed for real
        */
        requested = rMergedDuplicates;

        /*
            2. Remove duplicated `prioritized`, `executing` and `watching` callbacks
        */

        /*
            Extract all but the first callback from each IOS-key group
            these callbacks are `prioritized` and duplicates.
        */
        const pDuplicates = flatten(
            map(
                group => group.slice(0, -1),
                values(
                    groupBy<ICallback>(
                        getUniqueIdentifier,
                        concat(prioritized, requested)
                    )
                )
            )
        );

        const bDuplicates = flatten(
            map(
                group => group.slice(0, -1),
                values(
                    groupBy<ICallback>(
                        getUniqueIdentifier,
                        concat(blocked, requested)
                    )
                )
            )
        ) as IBlockedCallback[];

        const eDuplicates = flatten(
            map(
                group => group.slice(0, -1),
                values(
                    groupBy<ICallback>(
                        getUniqueIdentifier,
                        concat(executing, requested)
                    )
                )
            )
        ) as IExecutingCallback[];

        const wDuplicates = flatten(
            map(
                group => group.slice(0, -1),
                values(
                    groupBy<ICallback>(
                        getUniqueIdentifier,
                        concat(watched, requested)
                    )
                )
            )
        ) as IExecutingCallback[];

        /*
            3. Modify or remove callbacks that are outputting to non-existing layout `id`.
        */

        const {added: rAdded, removed: rRemoved} = pruneCallbacks(
            requested,
            paths
        );
        const {added: pAdded, removed: pRemoved} = pruneCallbacks(
            prioritized,
            paths
        );
        const {added: bAdded, removed: bRemoved} = pruneCallbacks(
            blocked,
            paths
        );
        const {added: eAdded, removed: eRemoved} = pruneCallbacks(
            executing,
            paths
        );
        const {added: wAdded, removed: wRemoved} = pruneCallbacks(
            watched,
            paths
        );

        /*
            TODO?
            Clean up the `requested` list - during the dispatch phase,
            it will be updated for real
        */
        requested = concat(difference(requested, rRemoved), rAdded);

        /*
            4. Find `requested` callbacks that do not depend on a outstanding output (as either input or state)
        */
        let readyCallbacks = getReadyCallbacks(
            paths,
            requested,
            pendingCallbacks,
            graphs
        );

        let oldBlocked: ICallback[] = [];
        let newBlocked: ICallback[] = [];

        /**
         * If there is :
         * - no ready callbacks
         * - at least one requested callback
         * - no additional pending callbacks
         *
         * can assume:
         * - the requested callbacks are part of a circular dependency loop
         *
         * then recursively:
         * - assume the first callback in the list is ready (the entry point for the loop)
         * - check what callbacks are blocked / ready with the assumption
         * - update the missing predecessors based on assumptions
         * - continue until there are no remaining candidates
         *
         */
        if (
            !readyCallbacks.length &&
            requested.length &&
            requested.length === pendingCallbacks.length
        ) {
            let candidates = requested.slice(0);

            while (candidates.length) {
                // Assume 1st callback is ready and
                // update candidates / readyCallbacks accordingly
                const readyCallback = candidates[0];

                readyCallbacks.push(readyCallback);
                candidates = candidates.slice(1);

                // Remaining candidates are not blocked by current assumptions
                candidates = getReadyCallbacks(
                    paths,
                    candidates,
                    readyCallbacks
                );

                // Blocked requests need to make sure they have the callback as a predecessor
                const blockedByAssumptions = difference(candidates, candidates);

                const modified = filter(
                    cb =>
                        !cb.predecessors ||
                        !includes(readyCallback.callback, cb.predecessors),
                    blockedByAssumptions
                );

                oldBlocked = concat(oldBlocked, modified);
                newBlocked = concat(
                    newBlocked,
                    modified.map(cb => ({
                        ...cb,
                        predecessors: concat(cb.predecessors ?? [], [
                            readyCallback.callback
                        ])
                    }))
                );
            }
        }

        /*
            TODO?
            Clean up the `requested` list - during the dispatch phase,
            it will be updated for real
        */
        requested = concat(difference(requested, oldBlocked), newBlocked);

        /*
            5. Prune callbacks that became irrelevant in their `executionGroup`
        */

        // Group by executionGroup, drop non-executionGroup callbacks
        // those were not triggered by layout changes and don't have "strong" interdependency for
        // callback chain completion
        const pendingGroups = groupBy<IStoredCallback>(
            cb => cb.executionGroup as any,
            filter(cb => !isNil(cb.executionGroup), stored)
        );

        const dropped: ICallback[] = filter(cb => {
            // If there is no `stored` callback for the group, no outputs were dropped -> `cb` is kept
            if (
                !cb.executionGroup ||
                !pendingGroups[cb.executionGroup] ||
                !pendingGroups[cb.executionGroup].length
            ) {
                return false;
            }

            // Get all inputs for `cb`
            const inputs = map(combineIdAndProp, flatten(cb.getInputs(paths)));

            // Get all the potentially updated props for the group so far
            const allProps = flatten(
                map(
                    gcb => gcb.executionMeta.allProps,
                    pendingGroups[cb.executionGroup]
                )
            );

            // Get all the updated props for the group so far
            const updated = flatten(
                map(
                    gcb => gcb.executionMeta.updatedProps,
                    pendingGroups[cb.executionGroup]
                )
            );

            // If there's no overlap between the updated props and the inputs,
            // + there's no props that aren't covered by the potentially updated props,
            // and not all inputs are multi valued
            // -> drop `cb`
            const res =
                isEmpty(intersection(inputs, updated)) &&
                isEmpty(difference(inputs, allProps)) &&
                !all(isMultiValued, cb.callback.inputs);

            return res;
        }, readyCallbacks);

        /*
            TODO?
            Clean up the `requested` list - during the dispatch phase,
            it will be updated for real
        */
        requested = difference(requested, dropped);

        readyCallbacks = difference(readyCallbacks, dropped);

        requested = difference(requested, readyCallbacks);

        const added = difference(requested, initialRequested);
        const removed = difference(initialRequested, requested);

        dispatch(
            aggregateCallbacks([
                // Clean up requested callbacks
                added.length ? addRequestedCallbacks(added) : null,
                removed.length ? removeRequestedCallbacks(removed) : null,
                // Clean up duplicated callbacks
                pDuplicates.length
                    ? removePrioritizedCallbacks(pDuplicates)
                    : null,
                bDuplicates.length ? removeBlockedCallbacks(bDuplicates) : null,
                eDuplicates.length
                    ? removeExecutingCallbacks(eDuplicates)
                    : null,
                wDuplicates.length ? removeWatchedCallbacks(wDuplicates) : null,
                // Prune callbacks
                pRemoved.length ? removePrioritizedCallbacks(pRemoved) : null,
                pAdded.length ? addPrioritizedCallbacks(pAdded) : null,
                bRemoved.length ? removeBlockedCallbacks(bRemoved) : null,
                bAdded.length ? addBlockedCallbacks(bAdded) : null,
                eRemoved.length ? removeExecutingCallbacks(eRemoved) : null,
                eAdded.length ? addExecutingCallbacks(eAdded) : null,
                wRemoved.length ? removeWatchedCallbacks(wRemoved) : null,
                wAdded.length ? addWatchedCallbacks(wAdded) : null,
                // Promote callbacks
                readyCallbacks.length
                    ? addPrioritizedCallbacks(readyCallbacks)
                    : null
            ])
        );
    },
    inputs: ['callbacks.requested', 'callbacks.completed']
};

export default observer;
