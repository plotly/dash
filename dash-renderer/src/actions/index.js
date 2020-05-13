import {
    concat,
    flatten,
    has,
    isEmpty,
    keys,
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
    pruneRemovedCallbacks,
    setNewRequestId,
    stringifyId,
    validateCallbacksToLayout,
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

export const dispatchError = dispatch => (message, lines) =>
    dispatch(
        onError({
            type: 'backEnd',
            error: {message, html: lines.join('\n')},
        })
    );

export function hydrateInitialOutputs() {
    return function(dispatch, getState) {
        validateCallbacksToLayout(getState(), dispatchError(dispatch));
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

            dispatch(notifyObservers({id, props}));
        }
    };
}

function unwrapIfNotMulti(paths, idProps, spec, anyVals, depType) {
    let msg = '';

    if (isMultiValued(spec)) {
        return [idProps, msg];
    }

    if (idProps.length !== 1) {
        if (!idProps.length) {
            const isStr = typeof spec.id === 'string';
            msg =
                'A nonexistent object was used in an `' +
                depType +
                '` of a Dash callback. The id of this object is ' +
                (isStr
                    ? '`' + spec.id + '`'
                    : JSON.stringify(spec.id) +
                      (anyVals ? ' with MATCH values ' + anyVals : '')) +
                ' and the property is `' +
                spec.property +
                (isStr
                    ? '`. The string ids in the current layout are: [' +
                      keys(paths.strs).join(', ') +
                      ']'
                    : '`. The wildcard ids currently available are logged above.');
        } else {
            msg =
                'Multiple objects were found for an `' +
                depType +
                '` of a callback that only takes one value. The id spec is ' +
                JSON.stringify(spec.id) +
                (anyVals ? ' with MATCH values ' + anyVals : '') +
                ' and the property is `' +
                spec.property +
                '`. The objects we found are: ' +
                JSON.stringify(map(pick(['id', 'property']), idProps));
        }
    }
    return [idProps[0], msg];
}

function startCallbacks(callbacks) {
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

    const allCallbacks = concat(requestedCallbacks, blockedCallbacks);
    dispatch(setPendingCallbacks(allCallbacks));

    const ids = requestedCallbacks.map(cb => [
        cb.getInputs(paths),
        cb.getState(paths),
    ]);
    await isAppReady(layout, paths, uniq(pluck('id', flatten(ids))));

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

        let payload;
        try {
            const inVals = fillVals(paths, layout, cb, inputs, 'Input', true);

            const preventCallback = () => {
                removeCallbackFromPending();
                // no server call here; for performance purposes pretend this is
                // a clientside callback and defer fireNext for the end
                // of the currently-ready callbacks.
                hasClientSide = true;
                return null;
            };

            if (inVals === null) {
                return preventCallback();
            }

            const outputs = [];
            const outputErrors = [];
            allOutputs.forEach((out, i) => {
                const [outi, erri] = unwrapIfNotMulti(
                    paths,
                    map(pick(['id', 'property']), out),
                    cb.callback.outputs[i],
                    cb.anyVals,
                    'Output'
                );
                outputs.push(outi);
                if (erri) {
                    outputErrors.push(erri);
                }
            });
            if (outputErrors.length) {
                if (flatten(inVals).length) {
                    refErr(outputErrors, paths);
                }
                // This case is all-empty multivalued wildcard inputs,
                // which we would normally fire the callback for, except
                // some outputs are missing. So instead we treat it like
                // regular missing inputs and just silently prevent it.
                return preventCallback();
            }

            payload = {
                output,
                outputs: isMultiOutputProp(output) ? outputs : outputs[0],
                inputs: inVals,
                changedPropIds: keys(cb.changedPropIds),
            };
            if (cb.callback.state.length) {
                payload.state = fillVals(paths, layout, cb, state, 'State');
            }
        } catch (e) {
            handleError(e);
            return fireNext();
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

                const {layout: oldLayout, paths: oldPaths} = getState();

                const appliedProps = doUpdateProps(
                    dispatch,
                    getState,
                    parsedId,
                    props
                );
                if (appliedProps) {
                    // doUpdateProps can cause new callbacks to be added
                    // via derived props - update pendingCallbacks
                    // But we may also need to merge in other callbacks that
                    // we found in an earlier interation of the data loop.
                    const statePendingCallbacks = getState().pendingCallbacks;
                    if (statePendingCallbacks !== pendingCallbacks) {
                        pendingCallbacks = mergePendingCallbacks(
                            pendingCallbacks,
                            statePendingCallbacks
                        );
                    }

                    Object.keys(appliedProps).forEach(property => {
                        updated.push(combineIdAndProp({id, property}));
                    });

                    if (has('children', appliedProps)) {
                        const oldChildren = path(
                            concat(getPath(oldPaths, parsedId), [
                                'props',
                                'children',
                            ]),
                            oldLayout
                        );
                        // If components changed, need to update paths,
                        // check if all pending callbacks are still
                        // valid, and add all callbacks associated with
                        // new components, either as inputs or outputs,
                        // or components removed from ALL/ALLSMALLER inputs
                        pendingCallbacks = updateChildPaths(
                            dispatch,
                            getState,
                            pendingCallbacks,
                            parsedId,
                            appliedProps.children,
                            oldChildren
                        );
                    }

                    // persistence edge case: if you explicitly update the
                    // persistence key, other props may change that require us
                    // to fire additional callbacks
                    const addedProps = pickBy(
                        (v, k) => !(k in props),
                        appliedProps
                    );
                    if (!isEmpty(addedProps)) {
                        const {graphs, paths} = getState();
                        pendingCallbacks = includeObservers(
                            id,
                            addedProps,
                            graphs,
                            paths,
                            pendingCallbacks
                        );
                    }
                }
            });
            updatePending(pendingCallbacks, without(updated, allPropIds));
        }

        function removeCallbackFromPending() {
            const {pendingCallbacks} = getState();
            if (requestIsActive(pendingCallbacks, resolvedId, requestId)) {
                // Skip all prop updates from this callback, and remove
                // it from the pending list so callbacks it was blocking
                // that have other changed inputs will still fire.
                updatePending(pendingCallbacks, allPropIds);
            }
        }

        function handleError(err) {
            removeCallbackFromPending();
            const outputs = payload
                ? map(combineIdAndProp, flatten([payload.outputs])).join(', ')
                : output;
            let message = `Callback error updating ${outputs}`;
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

function fillVals(paths, layout, cb, specs, depType, allowAllMissing) {
    const getter = depType === 'Input' ? cb.getInputs : cb.getState;
    const errors = [];
    let emptyMultiValues = 0;

    const inputVals = getter(paths).map((inputList, i) => {
        const [inputs, inputError] = unwrapIfNotMulti(
            paths,
            inputList.map(({id, property, path: path_}) => ({
                id,
                property,
                value: path(path_, layout).props[property],
            })),
            specs[i],
            cb.anyVals,
            depType
        );
        if (isMultiValued(specs[i]) && !inputs.length) {
            emptyMultiValues++;
        }
        if (inputError) {
            errors.push(inputError);
        }
        return inputs;
    });

    if (errors.length) {
        if (
            allowAllMissing &&
            errors.length + emptyMultiValues === inputVals.length
        ) {
            // We have at least one non-multivalued input, but all simple and
            // multi-valued inputs are missing.
            // (if all inputs are multivalued and all missing we still return
            // them as normal, and fire the callback.)
            return null;
        }
        // If we get here we have some missing and some present inputs.
        // Or all missing in a context that doesn't allow this.
        // That's a real problem, so throw the first message as an error.
        refErr(errors, paths);
    }

    return inputVals;
}

function refErr(errors, paths) {
    const err = errors[0];
    if (err.indexOf('logged above') !== -1) {
        // Wildcard reference errors mention a list of wildcard specs logged
        // TODO: unwrapped list of wildcard ids?
        // eslint-disable-next-line no-console
        console.error(paths.objs);
    }
    throw new ReferenceError(err);
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

function inputsToDict(inputs_list) {
    // Ported directly from _utils.py, inputs_to_dict
    // takes an array of inputs (some inputs may be an array)
    // returns an Object (map):
    //  keys of the form `id.property` or `{"id": 0}.property`
    //  values contain the property value
    if (!inputs_list) {
        return {};
    }
    const inputs = {};
    for (let i = 0; i < inputs_list.length; i++) {
        if (Array.isArray(inputs_list[i])) {
            const inputsi = inputs_list[i];
            for (let ii = 0; ii < inputsi.length; ii++) {
                const id_str = `${JSON.stringify(inputsi[ii].id)}.${
                    inputsi[ii].property
                }`;
                inputs[id_str] = inputsi[ii].value ? inputsi[ii].value : null;
            }
        } else {
            const id_str = `${inputs_list[i].id}.${inputs_list[i].property}`;
            inputs[id_str] = inputs_list[i].value ? inputs_list[i].value : null;
        }
    }
    return inputs;
}

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
        // setup callback context
        const input_dict = inputsToDict(inputs);
        dc.callback_context = {};
        if (payload.changedPropIds.length === 0) {
            dc.callback_context.triggered = [{prop_id: '.', value: null}];
        } else {
            dc.callback_context.triggered = payload.changedPropIds.map(
                prop_id => ({prop_id: prop_id, value: input_dict[prop_id]})
            );
        }
        dc.callback_context.inputs_list = inputs;
        dc.callback_context.inputs = input_dict;
        dc.callback_context.states_list = state;
        dc.callback_context.states = inputsToDict(state);

        const {namespace, function_name} = clientside_function;
        let args = inputs.map(getVals);
        if (state) {
            args = concat(args, state.map(getVals));
        }
        returnValue = dc[namespace][function_name](...args);

        delete dc.callback_context;
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

function updateChildPaths(
    dispatch,
    getState,
    pendingCallbacks,
    id,
    children,
    oldChildren
) {
    const {paths: oldPaths, graphs} = getState();
    const childrenPath = concat(getPath(oldPaths, id), ['props', 'children']);
    const paths = computePaths(children, childrenPath, oldPaths);
    dispatch(setPaths(paths));

    const cleanedCallbacks = pruneRemovedCallbacks(pendingCallbacks, paths);

    const newCallbacks = getCallbacksInLayout(graphs, paths, children, {
        chunkPath: childrenPath,
    });

    // Wildcard callbacks with array inputs (ALL / ALLSMALLER) need to trigger
    // even due to the deletion of components
    const deletedComponentCallbacks = getCallbacksInLayout(
        graphs,
        oldPaths,
        oldChildren,
        {removedArrayInputsOnly: true, newPaths: paths, chunkPath: childrenPath}
    );

    const allNewCallbacks = mergePendingCallbacks(
        newCallbacks,
        deletedComponentCallbacks
    );
    return mergePendingCallbacks(cleanedCallbacks, allNewCallbacks);
}

export function notifyObservers({id, props}) {
    return async function(dispatch, getState) {
        const {graphs, paths, pendingCallbacks} = getState();
        const finalCallbacks = includeObservers(
            id,
            props,
            graphs,
            paths,
            pendingCallbacks
        );
        dispatch(startCallbacks(finalCallbacks));
    };
}

function includeObservers(id, props, graphs, paths, pendingCallbacks) {
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
    return finalCallbacks;
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
