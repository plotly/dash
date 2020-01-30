/* global fetch:true, Promise:true, document:true */
import {
    assoc,
    concat,
    flatten,
    has,
    keys,
    lensPath,
    map,
    mergeDeepRight,
    once,
    path,
    pick,
    pickBy,
    pluck,
    propEq,
    type,
    uniq,
    view,
    without,
    zip,
} from 'ramda';
import {createAction} from 'redux-actions';
import {getAppState} from '../reducers/constants';
import {getAction} from './constants';
import cookie from 'cookie';
import {urlBase} from './utils';
import {
    combineIdAndProp,
    findReadyCallbacks,
    followForward,
    getCallbacksByInput,
    getCallbacksInLayout,
    isMultiOutputProp,
    isMultiValued,
    mergePendingCallbacks,
    removePendingCallback,
    parseIfWildcard,
    setNewRequestId,
    splitIdAndProp,
    stringifyId,
} from './dependencies';
import {computePaths, getPath} from './paths';
import {STATUS} from '../constants/constants';
import {applyPersistence, prunePersistence} from '../persistence';

import isAppReady from './isAppReady';

export const updateProps = createAction(getAction('ON_PROP_CHANGE'));
export const setPendingCallbacks = createAction('SET_PENDING_CALLBACKS');
export const setRequestQueue = createAction(getAction('SET_REQUEST_QUEUE'));
export const setGraphs = createAction(getAction('SET_GRAPHS'));
export const setPaths = createAction(getAction('SET_PATHS'));
export const setAppLifecycle = createAction(getAction('SET_APP_LIFECYCLE'));
export const setConfig = createAction(getAction('SET_CONFIG'));
export const setHooks = createAction(getAction('SET_HOOKS'));
export const setLayout = createAction(getAction('SET_LAYOUT'));
export const onError = createAction(getAction('ON_ERROR'));

export function hydrateInitialOutputs() {
    return function(dispatch, getState) {
        triggerDefaultState(dispatch, getState);
        dispatch(setAppLifecycle(getAppState('HYDRATED')));
    };
}

/* eslint-disable-next-line no-console */
const logWarningOnce = once(console.warn);

export function getCSRFHeader() {
    try {
        return {
            'X-CSRFToken': cookie.parse(document.cookie)._csrf_token,
        };
    } catch (e) {
        logWarningOnce(e);
        return {};
    }
}

function triggerDefaultState(dispatch, getState) {
    const {graphs, paths, layout} = getState();

    // overallOrder will assert circular dependencies for multi output.
    try {
        graphs.MultiGraph.overallOrder();
    } catch (err) {
        dispatch(
            onError({
                type: 'backEnd',
                error: {
                    message: 'Circular Dependencies',
                    html: err.toString(),
                },
            })
        );
    }

    const initialCallbacks = getCallbacksInLayout(graphs, paths, layout, {
        outputsOnly: true,
    });
    dispatch(startCallbacks(initialCallbacks));
}

export const redo = moveHistory('REDO');
export const undo = moveHistory('UNDO');
export const revert = moveHistory('REVERT');

function moveHistory(changeType) {
    return function(dispatch, getState) {
        const {history, paths} = getState();
        dispatch(createAction(changeType)());
        const {id, props} =
            (changeType === 'REDO'
                ? history.future[0]
                : history.past[history.past.length - 1]) || {};
        if (id) {
            // Update props
            dispatch(
                createAction('UNDO_PROP_CHANGE')({
                    itempath: getPath(paths, id),
                    props,
                })
            );

            // Notify observers
            dispatch(notifyObservers({id, props}));
        }
    };
}

function unwrapIfNotMulti(paths, idProps, spec, anyVals, depType) {
    if (isMultiValued(spec)) {
        return idProps;
    }
    if (idProps.length !== 1) {
        if (!idProps.length) {
            if (typeof spec.id === 'string') {
                throw new ReferenceError(
                    'A nonexistent object was used in an `' +
                        depType +
                        '` of a Dash callback. The id of this object is `' +
                        spec.id +
                        '` and the property is `' +
                        spec.property +
                        '`. The string ids in the current layout are: [' +
                        keys(paths.strs).join(', ') +
                        ']'
                );
            }
            // TODO: unwrapped list of wildcard ids?
            // eslint-disable-next-line no-console
            console.log(paths.objs);
            throw new ReferenceError(
                'A nonexistent object was used in an `' +
                    depType +
                    '` of a Dash callback. The id of this object is ' +
                    JSON.stringify(spec.id) +
                    (anyVals ? ' with ANY values ' + anyVals : '') +
                    ' and the property is `' +
                    spec.property +
                    '`. The wildcard ids currently available are logged above.'
            );
        }
        throw new ReferenceError(
            'Multiple objects were found for an `' +
                depType +
                '` of a callback that only takes one value. The id spec is ' +
                JSON.stringify(spec.id) +
                (anyVals ? ' with ANY values ' + anyVals : '') +
                ' and the property is `' +
                spec.property +
                '`. The objects we found are: ' +
                JSON.stringify(map(pick(['id', 'property']), idProps))
        );
    }
    return idProps[0];
}

export function startCallbacks(callbacks) {
    return async function(dispatch, getState) {
        return await fireReadyCallbacks(dispatch, getState, callbacks);
    };
}

async function fireReadyCallbacks(dispatch, getState, callbacks) {
    const {readyCallbacks, blockedCallbacks} = findReadyCallbacks(callbacks);
    const {config, hooks, layout, paths} = getState();

    // We want to calculate all the outputs only once, but we need them
    // for pendingCallbacks which we're going to dispatch prior to
    // initiating the queue. So first loop over readyCallbacks to
    // generate the output lists, then dispatch pendingCallbacks,
    // then loop again to fire off the requests.
    const outputStash = {};
    const requestedCallbacks = readyCallbacks.map(cb => {
        const cbOut = setNewRequestId(cb);

        const {requestId, getOutputs} = cbOut;
        const allOutputs = getOutputs(paths);
        const flatOutputs = flatten(allOutputs);
        const allPropIds = [];

        const reqOut = {};
        flatOutputs.forEach(({id, property}) => {
            const idStr = stringifyId(id);
            const idOut = (reqOut[idStr] = reqOut[idStr] || []);
            idOut.push(property);
            allPropIds.push(combineIdAndProp({id: idStr, property}));
        });
        cbOut.requestedOutputs = reqOut;

        outputStash[requestId] = {allOutputs, allPropIds};

        return cbOut;
    });

    const ids = uniq(
        pluck(
            'id',
            flatten(
                requestedCallbacks.map(cb =>
                    concat(cb.getInputs(paths), cb.getState(paths))
                )
            )
        )
    );

    await isAppReady(layout, paths, ids);

    const allCallbacks = concat(requestedCallbacks, blockedCallbacks);
    dispatch(setPendingCallbacks(allCallbacks));

    function fireNext() {
        return fireReadyCallbacks(
            dispatch,
            getState,
            getState().pendingCallbacks
        );
    }

    let hasClientSide = false;

    const queue = requestedCallbacks.map(cb => {
        const {output, inputs, state, clientside_function} = cb.callback;
        const {requestId, resolvedId} = cb;
        const {allOutputs, allPropIds} = outputStash[requestId];
        const outputs = allOutputs.map((out, i) =>
            unwrapIfNotMulti(
                paths,
                map(pick(['id', 'property']), out),
                cb.callback.outputs[i],
                cb.anyVals,
                'Output'
            )
        );

        const payload = {
            output,
            outputs: isMultiOutputProp(output) ? outputs : outputs[0],
            inputs: fillVals(paths, layout, cb, inputs, 'Input'),
            changedPropIds: keys(cb.changedPropIds),
        };
        if (cb.callback.state.length) {
            payload.state = fillVals(paths, layout, cb, state, 'State');
        }

        function updatePending(pendingCallbacks, skippedProps) {
            const newPending = removePendingCallback(
                pendingCallbacks,
                getState().paths,
                resolvedId,
                skippedProps
            );
            dispatch(setPendingCallbacks(newPending));
        }

        function handleData(data) {
            let {pendingCallbacks} = getState();
            if (!requestIsActive(pendingCallbacks, resolvedId, requestId)) {
                return;
            }
            const updated = [];
            Object.entries(data).forEach(([id, props]) => {
                const parsedId = parseIfWildcard(id);

                const appliedProps = doUpdateProps(
                    dispatch,
                    getState,
                    parsedId,
                    props
                );
                if (appliedProps) {
                    Object.keys(appliedProps).forEach(property => {
                        updated.push(combineIdAndProp({id, property}));
                    });

                    if (has('children', appliedProps)) {
                        // If components changed, need to update paths,
                        // check if all pending callbacks are still
                        // valid, and add all callbacks associated with
                        // new components, either as inputs or outputs
                        pendingCallbacks = updateChildPaths(
                            dispatch,
                            getState,
                            pendingCallbacks,
                            parsedId,
                            appliedProps.children
                        );
                    }
                }
            });
            updatePending(pendingCallbacks, without(updated, allPropIds));
        }

        function handleError(err) {
            const {pendingCallbacks} = getState();
            if (requestIsActive(pendingCallbacks, resolvedId, requestId)) {
                // Skip all prop updates from this callback, and remove
                // it from the pending list so callbacks it was blocking
                // that have other changed inputs will still fire.
                updatePending(pendingCallbacks, allPropIds);
            }
            let message = `Callback error updating ${JSON.stringify(
                payload.outputs
            )}`;
            if (clientside_function) {
                const {namespace: ns, function_name: fn} = clientside_function;
                message += ` via clientside function ${ns}.${fn}`;
            }
            handleAsyncError(err, message, dispatch);
        }

        if (clientside_function) {
            try {
                handleData(handleClientside(clientside_function, payload));
            } catch (err) {
                handleError(err);
            }
            hasClientSide = true;
            return null;
        }

        return handleServerside(config, payload, hooks)
            .then(handleData)
            .catch(handleError)
            .then(fireNext);
    });
    const done = Promise.all(queue);
    return hasClientSide ? fireNext().then(done) : done;
}

function fillVals(paths, layout, cb, specs, depType) {
    const getter = depType === 'Input' ? cb.getInputs : cb.getState;
    return getter(paths).map((inputList, i) =>
        unwrapIfNotMulti(
            paths,
            inputList.map(({id, property, path: path_}) => ({
                id,
                property,
                value: path(path_, layout).props[property],
            })),
            specs[i],
            cb.anyVals,
            depType
        )
    );
}

function handleServerside(config, payload, hooks) {
    if (hooks.request_pre !== null) {
        hooks.request_pre(payload);
    }

    return fetch(
        `${urlBase(config)}_dash-update-component`,
        mergeDeepRight(config.fetch, {
            method: 'POST',
            headers: getCSRFHeader(),
            body: JSON.stringify(payload),
        })
    ).then(res => {
        const {status} = res;
        if (status === STATUS.OK) {
            return res.json().then(data => {
                const {multi, response} = data;
                if (hooks.request_post !== null) {
                    hooks.request_post(payload, response);
                }

                if (multi) {
                    return response;
                }

                const {output} = payload;
                const id = output.substr(0, output.lastIndexOf('.'));
                return {[id]: response.props};
            });
        }
        if (status === STATUS.PREVENT_UPDATE) {
            return {};
        }
        throw res;
    });
}

const getVals = input =>
    Array.isArray(input) ? pluck('value', input) : input.value;

const zipIfArray = (a, b) => (Array.isArray(a) ? zip(a, b) : [[a, b]]);

function handleClientside(clientside_function, payload) {
    const dc = (window.dash_clientside = window.dash_clientside || {});
    if (!dc.no_update) {
        Object.defineProperty(dc, 'no_update', {
            value: {description: 'Return to prevent updating an Output.'},
            writable: false,
        });

        Object.defineProperty(dc, 'PreventUpdate', {
            value: {description: 'Throw to prevent updating all Outputs.'},
            writable: false,
        });
    }

    const {inputs, outputs, state} = payload;

    let returnValue;

    try {
        const {namespace, function_name} = clientside_function;
        let args = inputs.map(getVals);
        if (state) {
            args = concat(args, state.map(getVals));
        }
        returnValue = dc[namespace][function_name](...args);
    } catch (e) {
        if (e === dc.PreventUpdate) {
            return {};
        }
        throw e;
    }

    if (type(returnValue) === 'Promise') {
        throw new Error(
            'The clientside function returned a Promise. ' +
                'Promises are not supported in Dash clientside ' +
                'right now, but may be in the future.'
        );
    }

    const data = {};
    zipIfArray(outputs, returnValue).forEach(([outi, reti]) => {
        zipIfArray(outi, reti).forEach(([outij, retij]) => {
            const {id, property} = outij;
            const idStr = stringifyId(id);
            const dataForId = (data[idStr] = data[idStr] || {});
            if (retij !== dc.no_update) {
                dataForId[property] = retij;
            }
        });
    });
    return data;
}

function requestIsActive(pendingCallbacks, resolvedId, requestId) {
    const thisCallback = pendingCallbacks.find(
        propEq('resolvedId', resolvedId)
    );
    // could be inactivated if it was requested again, in which case it could
    // potentially even have finished and been removed from the list
    return thisCallback && thisCallback.requestId === requestId;
}

function doUpdateProps(dispatch, getState, id, updatedProps) {
    const {layout, paths} = getState();
    const itempath = getPath(paths, id);
    if (!itempath) {
        return false;
    }

    // This is a callback-generated update.
    // Check if this invalidates existing persisted prop values,
    // or if persistence changed, whether this updates other props.
    const updatedProps2 = prunePersistence(
        path(itempath, layout),
        updatedProps,
        dispatch
    );

    // In case the update contains whole components, see if any of
    // those components have props to update to persist user edits.
    const {props} = applyPersistence({props: updatedProps2}, dispatch);

    dispatch(
        updateProps({
            itempath,
            props,
            source: 'response',
        })
    );

    return props;
}

function updateChildPaths(dispatch, getState, pendingCallbacks, id, children) {
    const {paths: oldPaths, graphs} = getState();
    const childrenPath = concat(getPath(oldPaths, id), ['props', 'children']);
    const paths = computePaths(children, childrenPath, oldPaths);
    dispatch(setPaths(paths));

    // Prune now-nonexistent changedPropIds and mark callbacks with
    // now-nonexistent outputs
    const removeIds = [];
    let cleanedCallbacks = pendingCallbacks.map(callback => {
        const {changedPropIds, getOutputs, resolvedId} = callback;
        if (!flatten(getOutputs(paths)).length) {
            removeIds.push(resolvedId);
            return callback;
        }

        let omittedProps = false;
        const newChangedProps = pickBy((_, propId) => {
            if (getPath(paths, splitIdAndProp(propId).id)) {
                return true;
            }
            omittedProps = true;
            return false;
        }, changedPropIds);

        return omittedProps
            ? assoc('changedPropIds', newChangedProps, callback)
            : callback;
    });

    // Remove the callbacks we marked above
    removeIds.forEach(resolvedId => {
        const cb = cleanedCallbacks.find(propEq('resolvedId', resolvedId));
        if (cb) {
            cleanedCallbacks = removePendingCallback(
                pendingCallbacks,
                paths,
                resolvedId,
                flatten(cb.getOutputs(paths)).map(combineIdAndProp)
            );
        }
    });

    const newCallbacks = getCallbacksInLayout(graphs, paths, children);
    return mergePendingCallbacks(cleanedCallbacks, newCallbacks);
}

export function notifyObservers({id, props}) {
    return async function(dispatch, getState) {
        const {graphs, paths, pendingCallbacks} = getState();

        const changedProps = keys(props);
        let finalCallbacks = pendingCallbacks;

        changedProps.forEach(propName => {
            const newCBs = getCallbacksByInput(graphs, paths, id, propName);
            if (newCBs.length) {
                finalCallbacks = mergePendingCallbacks(
                    finalCallbacks,
                    followForward(graphs, paths, newCBs)
                );
            }
        });
        dispatch(startCallbacks(finalCallbacks));
    };
}

export function handleAsyncError(err, message, dispatch) {
    // Handle html error responses
    if (err && typeof err.text === 'function') {
        err.text().then(text => {
            const error = {message, html: text};
            dispatch(onError({type: 'backEnd', error}));
        });
    } else {
        const error = err instanceof Error ? err : {message, html: err};
        dispatch(onError({type: 'backEnd', error}));
    }
}

export function serialize(state) {
    // Record minimal input state in the url
    const {graphs, paths, layout} = state;
    const {InputGraph} = graphs;
    const allNodes = InputGraph.nodes;
    const savedState = {};
    keys(allNodes).forEach(nodeId => {
        const [componentId, componentProp] = nodeId.split('.');
        /*
         * Filter out the outputs,
         * and the invisible inputs
         */
        if (
            InputGraph.dependenciesOf(nodeId).length > 0 &&
            has(componentId, paths)
        ) {
            // Get the property
            const propLens = lensPath(
                concat(paths[componentId], ['props', componentProp])
            );
            const propValue = view(propLens, layout);
            savedState[nodeId] = propValue;
        }
    });

    return savedState;
}
