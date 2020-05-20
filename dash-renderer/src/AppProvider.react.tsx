import {
    all,
    assoc,
    concat,
    difference,
    filter,
    find,
    flatten,
    forEach,
    groupBy,
    has,
    includes,
    intersection,
    isEmpty,
    isNil,
    keys,
    map,
    partition,
    path,
    pickBy,
    pluck,
    reduce,
    toPairs,
    uniq,
    values
} from 'ramda';

import React from 'react';
import {Provider} from 'react-redux';

import initializeStore, { observe } from './store';
import AppContainer from './AppContainer.react';

import PropTypes from 'prop-types';
import {
    handleAsyncError,
    setPaths,
    updateProps
} from './actions';
import {
    addCompletedCallbacks,
    addExecutedCallbacks,
    addExecutingCallbacks,
    addPrioritizedCallbacks,
    addRequestedCallbacks,
    addStoredCallbacks,
    addWatchedCallbacks,
    aggregateCallbacks,
    executeCallback,
    removeExecutedCallbacks,
    removeExecutingCallbacks,
    removePrioritizedCallbacks,
    removeRequestedCallbacks,
    removeStoredCallbacks,
    removeWatchedCallbacks,
    setPendingCallbacks
} from './actions/callbacks';
import { getPath, computePaths } from './actions/paths';

import {
    getCallbacksByInput,
    parseIfWildcard,
    stringifyId,
    isMultiValued
} from './actions/dependencies';
import {
    combineIdAndProp,
    getLayoutCallbacks,
    getReadyCallbacks,
    getUniqueIdentifier,
    includeObservers,
    pruneCallbacks
} from './actions/dependencies_ts';
import { ICallbacksState } from './reducers/callbacks';
import {
    IExecutingCallback,
    ICallback,
    ICallbackProperty,
    IStoredCallback
} from './types/callbacks';
import isAppReady from './actions/isAppReady';
import {
    applyPersistence,
    prunePersistence
} from './persistence';

const store = initializeStore();

const getPendingCallbacks = ({ executed, executing, prioritized, requested, watched }: ICallbacksState) => [
    ...requested,
    ...prioritized,
    ...executing,
    ...watched,
    ...executed
];

observe(({
    dispatch,
    getState
}) => {
    const {
        callbacks,
        pendingCallbacks
    } = getState();

    const next = getPendingCallbacks(callbacks);

    /**
     * If the calculated list of pending callbacks is equivalent
     * to the previous one, do not update it.
     */
    if (
        pendingCallbacks &&
        pendingCallbacks.length === next.length &&
        next.every((v, i) =>
            v === pendingCallbacks[i] ||
            v.callback === pendingCallbacks[i].callback)
    ) {
        return;
    }

    dispatch(setPendingCallbacks(next));
}, ['callbacks']);

observe(({
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
}, ['callbacks.requested', 'callbacks.completed']);

observe(async ({
    dispatch,
    getState
}) => {
    const { callbacks: { executing, watched }, config, hooks, layout, paths } = getState();
    let { callbacks: { prioritized } } = getState();

    console.log('onCallbacksChanged.prioritized', prioritized);

    const available = Math.max(
        0,
        6 - executing.length - watched.length
    );

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
        ...cb.getInputs(paths),
        ...cb.getState(paths)
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

}, ['callbacks.prioritized', 'callbacks.completed']);

observe(({
    dispatch,
    getState
}) => {
    const {
        callbacks: {
            executing
        },
    } = getState();

    console.log('onCallbacksChanged.executing', executing);

    const [deferred, skippedOrReady] = partition(cb => cb.executionPromise instanceof Promise, executing);

    dispatch(aggregateCallbacks([
        executing.length ? removeExecutingCallbacks(executing) : null,
        deferred.length ? addWatchedCallbacks(deferred) : null,
        skippedOrReady.length ? addExecutedCallbacks(skippedOrReady.map(cb => assoc('executionResult', cb.executionPromise as any, cb))) : null
    ]));

    deferred.forEach(async function (cb: IExecutingCallback) {
        const result = await cb.executionPromise;

        /*
            Check if it's been removed from the `watched` list since - on callback completion, another callback may be cancelled
        */
        const { callbacks: { watched } } = getState();

        /*
            Find the callback instance or one that matches its promise (eg. could have been pruned)
        */
        const currentCb = find(_cb => _cb === cb || _cb.executionPromise === cb.executionPromise, watched);
        if (!currentCb) {
            return;
        }

        /*
            Otherwise move to `executed` and remove from `watched`
        */
        dispatch(aggregateCallbacks([
            removeWatchedCallbacks([currentCb]),
            addExecutedCallbacks([{
                ...currentCb,
                executionResult: result
            }])
        ]));
    });
}, ['callbacks.executing']);

observe(({
    dispatch,
    getState
}) => {
    const {
        callbacks: {
            executed
        }
    } = getState();

    function applyProps(id: any, updatedProps: any) {
        const { layout, paths } = getState();
        const itempath = getPath(paths, id);
        if (!itempath) {
            return false;
        }

        // This is a callback-generated update.
        // Check if this invalidates existing persisted prop values,
        // or if persistence changed, whether this updates other props.
        updatedProps = prunePersistence(
            path(itempath, layout),
            updatedProps,
            dispatch
        );

        // In case the update contains whole components, see if any of
        // those components have props to update to persist user edits.
        const { props } = applyPersistence({ props: updatedProps }, dispatch);

        dispatch(
            updateProps({
                itempath,
                props,
                source: 'response',
            })
        );

        return props;
    }

    console.log('onCallbacksChanged.executed', executed);

    let requestedCallbacks: ICallback[] = [];
    let storedCallbacks: IStoredCallback[] = [];

    forEach(cb => {
        const { executionResult } = cb;

        if (isNil(executionResult)) {
            return;
        }

        const { data, error } = executionResult;
        console.log('onCallbacksChanged.executed', '[executionResult]', cb, data);

        if (data !== undefined) {
            forEach(([id, props]: [any, { [key: string]: any }]) => {
                const parsedId = parseIfWildcard(id);
                const { graphs, layout: oldLayout, paths: oldPaths } = getState();

                // Components will trigger callbacks on their own as required (eg. derived)
                const appliedProps = applyProps(parsedId, props);

                // Skip prop-triggered callbacks for callbacks with an execution group - these callbacks
                // should already be present in `requested`
                requestedCallbacks = concat(
                    requestedCallbacks,
                    flatten(map(
                        prop => getCallbacksByInput(graphs, oldPaths, parsedId, prop),
                        keys(props)
                    ))
                );

                // New layout - trigger callbacks for that explicitly
                if (has('children', appliedProps)) {
                    const { children } = appliedProps;

                    const oldChildrenPath: string[] = concat(getPath(oldPaths, parsedId) as string[], ['props', 'children']);
                    const oldChildren = path(oldChildrenPath, oldLayout);

                    const paths = computePaths(children, oldChildrenPath, oldPaths);
                    dispatch(setPaths(paths));

                    requestedCallbacks = concat(
                        requestedCallbacks,
                        getLayoutCallbacks(graphs, paths, children, {
                            chunkPath: oldChildrenPath,
                        })
                    );

                    // Wildcard callbacks with array inputs (ALL / ALLSMALLER) need to trigger
                    // even due to the deletion of components
                    requestedCallbacks = concat(
                        requestedCallbacks,
                        getLayoutCallbacks(graphs, oldPaths, oldChildren, {
                            removedArrayInputsOnly: true, newPaths: paths, chunkPath: oldChildrenPath
                        })
                    );
                }

                // persistence edge case: if you explicitly update the
                // persistence key, other props may change that require us
                // to fire additional callbacks
                const addedProps = pickBy(
                    (_, k) => !(k in props),
                    appliedProps
                );
                if (!isEmpty(addedProps)) {
                    const { graphs, paths } = getState();

                    requestedCallbacks = concat(
                        requestedCallbacks,
                        includeObservers(id, addedProps, graphs, paths)
                    );
                }
            }, Object.entries(data));



            storedCallbacks.push({
                ...cb,
                executionMeta: {
                    allProps: map(combineIdAndProp, flatten(cb.getOutputs(getState().paths))),
                    updatedProps: flatten(map(
                        ([id, value]) => map(
                            property => combineIdAndProp({ id, property }),
                            keys(value)
                        ),
                        toPairs(data)
                    ))
                }
            });
        }

        if (error !== undefined) {
            handleAsyncError(error, error.message, dispatch);

            storedCallbacks.push({
                ...cb,
                executionMeta: {
                    allProps: map(combineIdAndProp, flatten(cb.getOutputs(getState().paths))),
                    updatedProps: []
                }
            });
        }
    }, executed);

    console.log('SPECIAL', '[requestedCallbacks]', requestedCallbacks);
    dispatch(aggregateCallbacks([
        executed.length ? removeExecutedCallbacks(executed) : null,
        executed.length ? addCompletedCallbacks(executed.length) : null,
        storedCallbacks.length ? addStoredCallbacks(storedCallbacks) : null,
        requestedCallbacks.length ? addRequestedCallbacks(requestedCallbacks) : null
    ]));
}, ['callbacks.executed']);

observe(({
    dispatch,
    getState
}) => {
    const { callbacks } = getState();
    const pendingCallbacks = getPendingCallbacks(callbacks);

    let { callbacks: { stored } } = getState();

    console.log('onCallbacksChanged.stored', stored);

    const [nullGroupCallbacks, groupCallbacks] = partition(
        cb => isNil(cb.executionGroup),
        stored
    );

    const executionGroups = groupBy<IStoredCallback>(
        cb => cb.executionGroup as any,
        groupCallbacks
    )

    const pendingGroups = groupBy<ICallback>(
        cb => cb.executionGroup as any,
        filter(cb => !isNil(cb.executionGroup), pendingCallbacks)
    );

    let dropped = reduce((res, [
        executionGroup,
        callbacks
    ]) => !pendingGroups[executionGroup] ?
            concat(res, callbacks) :
            res,
        [] as IStoredCallback[],
        toPairs(executionGroups)
    );

    console.log('onCallbacksChanged.stored', '[dropped]', nullGroupCallbacks, dropped);

    dispatch(aggregateCallbacks([
        nullGroupCallbacks.length ? removeStoredCallbacks(nullGroupCallbacks) : null,
        dropped.length ? removeStoredCallbacks(dropped): null
    ]));
}, ['callbacks.stored', 'callbacks.completed'])

const AppProvider = ({hooks}: any) => {
    return (
        <Provider store={store}>
            <AppContainer hooks={hooks} />
        </Provider>
    );
};

AppProvider.propTypes = {
    hooks: PropTypes.shape({
        request_pre: PropTypes.func,
        request_post: PropTypes.func,
    }),
};

AppProvider.defaultProps = {
    hooks: {
        request_pre: null,
        request_post: null,
    },
};

export default AppProvider;


