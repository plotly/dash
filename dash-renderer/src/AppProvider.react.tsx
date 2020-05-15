import {
    assoc,
    concat,
    difference,
    find,
    flatten,
    forEach,
    groupBy,
    has,
    includes,
    isEmpty,
    isNil,
    keys,
    map,
    partition,
    path,
    pickBy,
    pluck,
    reduce,
    uniq,
    values
} from 'ramda';

import React from 'react';
import {Provider} from 'react-redux';

import initializeStore, { observe } from './store';
import AppContainer from './AppContainer.react';

import PropTypes from 'prop-types';
import {
    updateProps,
    setPaths,
    handleAsyncError
} from './actions';
import {
    addCompletedCallbacks,
    addExecutedCallbacks,
    addExecutingCallbacks,
    addPrioritizedCallbacks,
    addRequestedCallbacks,
    addWatchedCallbacks,
    aggregateCallbacks,
    executeCallback,
    removeExecutedCallbacks,
    removeExecutingCallbacks,
    removePrioritizedCallbacks,
    removeRequestedCallbacks,
    removeWatchedCallbacks,
    setPendingCallbacks
} from './actions/callbacks';
import { getPath, computePaths } from './actions/paths';

import { stringifyId, parseIfWildcard, getCallbacksByInput } from './actions/dependencies';
import { combineIdAndProp, getUniqueIdentifier, includeObservers, pruneCallbacks, getReadyCallbacks, getLayoutCallbacks } from './actions/dependencies_ts';
import { ICallbacksState } from './reducers/callbacks';
import { IExecutingCallback, ICallback, ICallbackProperty } from './types/callbacks';
import isAppReady from './actions/isAppReady';
import { prunePersistence, applyPersistence } from './persistence';

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
    console.log('onCallbacksChanged', '[pendingCallbacks-candidate]', callbacks, next);

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

    console.log('onCallbacksChanged', '[pendingCallbacks]', next);
    dispatch(setPendingCallbacks(next));
}, ['callbacks']);

observe(({
    dispatch,
    getState
}) => {
    const { callbacks, callbacks: { prioritized, executing, watched, executed, completed }, paths } = getState();
    let { callbacks: { requested } } = getState();

    const pendingCallbacks = getPendingCallbacks(callbacks);

    console.log('onCallbacksChanged.requested', completed, requested);

    /*
        1. Remove duplicated `requested` callbacks
    */

    /*
        Extract all but the first callback from each IOS-key group
        these callbacks are duplicates.
    */
    const rDuplicates = flatten(map(
        group => group.slice(1),
        values(
            groupBy<ICallback>(
                getUniqueIdentifier,
                requested
            )
        )
    ));

    /*
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
        group => group.slice(1),
        values(
            groupBy<ICallback>(
                getUniqueIdentifier,
                concat(requested, prioritized)
            )
        )
    ));

    const eDuplicates = flatten(map(
        group => group.slice(1),
        values(
            groupBy<ICallback>(
                getUniqueIdentifier,
                concat(requested, executing)
            )
        )
    )) as IExecutingCallback[];

    const wDuplicates = flatten(map(
        group => group.slice(1),
        values(
            groupBy<ICallback>(
                getUniqueIdentifier,
                concat(requested, watched)
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
    const readyCallbacks = getReadyCallbacks(requested, pendingCallbacks);

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
    const [remainingCallbacks, droppedCallbacks] = partition(
        ([cb]) => includes(cb, updatedPrioritized),
        callbacks
    );

    if (droppedCallbacks.length) {
        console.log('onCallbacksChanged.prioritized', '[dropped]', map(([cb]) => cb, droppedCallbacks));
    }

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

    let callbacks: ICallback[] = [];
    forEach(({ executionResult }) => {
        if (isNil(executionResult)) {
            return;
        }

        const { data, error } = executionResult;
        console.log('SPECIAL', '[executionResult]', data);

        if (data !== undefined) {
            return forEach(([id, props]: [any, { [key: string]: any }]) => {
                const parsedId = parseIfWildcard(id);
                const { graphs, layout: oldLayout, paths: oldPaths } = getState();

                // Components will trigger callbacks on their own as required (eg. derived)
                const appliedProps = applyProps(parsedId, props);

                callbacks = concat(
                    callbacks,
                    flatten(map(
                        prop => getCallbacksByInput(graphs, oldPaths, parsedId, prop),
                        keys(props)
                    ))
                )

                // New layout - trigger callbacks for that explicitly
                if (has('children', appliedProps)) {
                    const { children } = appliedProps;

                    const oldChildrenPath: string[] = concat(getPath(oldPaths, parsedId) as string[], ['props', 'children']);
                    const oldChildren = path(oldChildrenPath, oldLayout);

                    const paths = computePaths(children, oldChildrenPath, oldPaths);
                    dispatch(setPaths(paths));

                    callbacks = concat(
                        callbacks,
                        getLayoutCallbacks(graphs, paths, children, {
                            chunkPath: oldChildrenPath,
                        })
                    );

                    // Wildcard callbacks with array inputs (ALL / ALLSMALLER) need to trigger
                    // even due to the deletion of components
                    callbacks = concat(
                        callbacks,
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

                    callbacks = concat(
                        callbacks,
                        includeObservers(id, addedProps, graphs, paths)
                    );
                }

            }, Object.entries(data));
        }

        if (error !== undefined) {
            handleAsyncError(error, error.message, dispatch);
        }
    }, executed);

    dispatch(aggregateCallbacks([
        executed.length ? removeExecutedCallbacks(executed) : null,
        executed.length ? addCompletedCallbacks(executed.length) : null,
        callbacks.length ? addRequestedCallbacks(callbacks) : null
    ]));
}, ['callbacks.executed']);

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


