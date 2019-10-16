/* global fetch:true, Promise:true, document:true */
import {
    adjust,
    any,
    append,
    concat,
    findIndex,
    findLastIndex,
    flatten,
    flip,
    has,
    includes,
    intersection,
    isEmpty,
    keys,
    lensPath,
    mergeLeft,
    mergeDeepRight,
    path,
    pluck,
    propEq,
    reject,
    slice,
    sort,
    type,
    view,
} from 'ramda';
import {createAction} from 'redux-actions';
import {crawlLayout, hasId} from '../reducers/utils';
import {getAppState} from '../reducers/constants';
import {getAction} from './constants';
import cookie from 'cookie';
import {uid, urlBase, isMultiOutputProp, parseMultipleOutputs} from '../utils';
import {STATUS} from '../constants/constants';
import {applyPersistence, prunePersistence} from '../persistence';

export const updateProps = createAction(getAction('ON_PROP_CHANGE'));
export const setRequestQueue = createAction(getAction('SET_REQUEST_QUEUE'));
export const computeGraphs = createAction(getAction('COMPUTE_GRAPHS'));
export const computePaths = createAction(getAction('COMPUTE_PATHS'));
export const setLayout = createAction(getAction('SET_LAYOUT'));
export const setAppLifecycle = createAction(getAction('SET_APP_LIFECYCLE'));
export const setConfig = createAction(getAction('SET_CONFIG'));
export const setHooks = createAction(getAction('SET_HOOKS'));
export const onError = createAction(getAction('ON_ERROR'));

export function hydrateInitialOutputs() {
    return function(dispatch, getState) {
        triggerDefaultState(dispatch, getState);
        dispatch(setAppLifecycle(getAppState('HYDRATED')));
    };
}

export function getCSRFHeader() {
    return {
        'X-CSRFToken': cookie.parse(document.cookie)._csrf_token,
    };
}

function triggerDefaultState(dispatch, getState) {
    const {graphs} = getState();
    const {InputGraph, MultiGraph} = graphs;
    const allNodes = InputGraph.overallOrder();
    // overallOrder will assert circular dependencies for multi output.

    try {
        MultiGraph.overallOrder();
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

    const inputNodeIds = [];
    allNodes.reverse();
    allNodes.forEach(nodeId => {
        const componentId = nodeId.split('.')[0];
        /*
         * Filter out the outputs,
         * inputs that aren't leaves,
         * and the invisible inputs
         */
        if (
            InputGraph.dependenciesOf(nodeId).length > 0 &&
            InputGraph.dependantsOf(nodeId).length === 0 &&
            has(componentId, getState().paths)
        ) {
            inputNodeIds.push(nodeId);
        }
    });

    reduceInputIds(inputNodeIds, InputGraph).forEach(inputOutput => {
        const [componentId, componentProp] = inputOutput.input.split('.');
        // Get the initial property
        const propLens = lensPath(
            concat(getState().paths[componentId], ['props', componentProp])
        );
        const propValue = view(propLens, getState().layout);

        dispatch(
            notifyObservers({
                id: componentId,
                props: {[componentProp]: propValue},
                excludedOutputs: inputOutput.excludedOutputs,
            })
        );
    });
}

export function redo() {
    return function(dispatch, getState) {
        const history = getState().history;
        dispatch(createAction('REDO')());
        const next = history.future[0];

        // Update props
        dispatch(
            createAction('REDO_PROP_CHANGE')({
                itempath: getState().paths[next.id],
                props: next.props,
            })
        );

        // Notify observers
        dispatch(
            notifyObservers({
                id: next.id,
                props: next.props,
            })
        );
    };
}

const UNDO = createAction('UNDO')();
export function undo() {
    return undo_revert(UNDO);
}

const REVERT = createAction('REVERT')();
export function revert() {
    return undo_revert(REVERT);
}

function undo_revert(undo_or_revert) {
    return function(dispatch, getState) {
        const history = getState().history;
        dispatch(undo_or_revert);
        const previous = history.past[history.past.length - 1];

        // Update props
        dispatch(
            createAction('UNDO_PROP_CHANGE')({
                itempath: getState().paths[previous.id],
                props: previous.props,
            })
        );

        // Notify observers
        dispatch(
            notifyObservers({
                id: previous.id,
                props: previous.props,
            })
        );
    };
}

function reduceInputIds(nodeIds, InputGraph) {
    /*
     * Create input-output(s) pairs,
     * sort by number of outputs,
     * and remove redudant inputs (inputs that update the same output)
     */
    const inputOutputPairs = nodeIds.map(nodeId => ({
        input: nodeId,
        // TODO - Does this include grandchildren?
        outputs: InputGraph.dependenciesOf(nodeId),
        excludedOutputs: [],
    }));

    const sortedInputOutputPairs = sort(
        (a, b) => b.outputs.length - a.outputs.length,
        inputOutputPairs
    );

    /*
     * In some cases, we may have unique outputs but inputs that could
     * trigger components to update multiple times.
     *
     * For example, [A, B] => C and [A, D] => E
     * The unique inputs might be [A, B, D] but that is redudant.
     * We only need to update B and D or just A.
     *
     * In these cases, we'll supply an additional list of outputs
     * to exclude.
     */
    sortedInputOutputPairs.forEach((pair, i) => {
        const outputsThatWillBeUpdated = flatten(
            pluck('outputs', slice(0, i, sortedInputOutputPairs))
        );
        pair.outputs.forEach(output => {
            if (includes(output, outputsThatWillBeUpdated)) {
                pair.excludedOutputs.push(output);
            }
        });
    });

    return sortedInputOutputPairs;
}

export function notifyObservers(payload) {
    return function(dispatch, getState) {
        const {id, props, excludedOutputs} = payload;

        const {graphs, requestQueue} = getState();
        const {InputGraph} = graphs;
        /*
         * Figure out all of the output id's that depend on this input.
         * This includes id's that are direct children as well as
         * grandchildren.
         * grandchildren will get filtered out in a later stage.
         */
        let outputObservers = [];

        const changedProps = keys(props);
        changedProps.forEach(propName => {
            const node = `${id}.${propName}`;
            if (!InputGraph.hasNode(node)) {
                return;
            }
            InputGraph.dependenciesOf(node).forEach(outputId => {
                /*
                 * Multiple input properties that update the same
                 * output can change at once.
                 * For example, `n_clicks` and `n_clicks_previous`
                 * on a button component.
                 * We only need to update the output once for this
                 * update, so keep outputObservers unique.
                 */
                if (!includes(outputId, outputObservers)) {
                    outputObservers.push(outputId);
                }
            });
        });

        if (excludedOutputs) {
            outputObservers = reject(
                flip(includes)(excludedOutputs),
                outputObservers
            );
        }

        if (isEmpty(outputObservers)) {
            return;
        }

        /*
         * There may be several components that depend on this input.
         * And some components may depend on other components before
         * updating. Get this update order straightened out.
         */
        const depOrder = InputGraph.overallOrder();
        outputObservers = sort(
            (a, b) => depOrder.indexOf(b) - depOrder.indexOf(a),
            outputObservers
        );
        const queuedObservers = [];
        outputObservers.forEach(function filterObservers(outputIdAndProp) {
            let outputIds;
            if (isMultiOutputProp(outputIdAndProp)) {
                outputIds = parseMultipleOutputs(outputIdAndProp).map(
                    e => e.split('.')[0]
                );
            } else {
                outputIds = [outputIdAndProp.split('.')[0]];
            }

            /*
             * before we make the POST to update the output, check
             * that the output doesn't depend on any other inputs that
             * that depend on the same controller.
             * if the output has another input with a shared controller,
             * then don't update this output yet.
             * when each dependency updates, it'll dispatch its own
             * `notifyObservers` action which will allow this
             * component to update.
             *
             * for example, if A updates B and C (A -> [B, C]) and B updates C
             * (B -> C), then when A updates, this logic will
             * reject C from the queue since it will end up getting updated
             * by B.
             *
             * in this case, B will already be in queuedObservers by the time
             * this loop hits C because of the overallOrder sorting logic
             */

            const controllers = InputGraph.dependantsOf(outputIdAndProp);

            const controllersInFutureQueue = intersection(
                queuedObservers,
                controllers
            );

            /*
             * check that the output hasn't been triggered to update already
             * by a different input.
             *
             * for example:
             * Grandparent -> [Parent A, Parent B] -> Child
             *
             * when Grandparent changes, it will trigger Parent A and Parent B
             * to each update Child.
             * one of the components (Parent A or Parent B) will queue up
             * the change for Child. if this update has already been queued up,
             * then skip the update for the other component
             */
            const controllerIsInExistingQueue = any(
                r =>
                    includes(r.controllerId, controllers) &&
                    r.status === 'loading',
                requestQueue
            );

            /*
             * TODO - Place throttling logic here?
             *
             * Only process the last two requests for a _single_ output
             * at a time.
             *
             * For example, if A -> B, and A is changed 10 times, then:
             * 1 - processing the first two requests
             * 2 - if more than 2 requests come in while the first two
             *     are being processed, then skip updating all of the
             *     requests except for the last 2
             */

            /*
             * also check that this observer is actually in the current
             * component tree.
             * observers don't actually need to be rendered at the moment
             * of a controller change.
             * for example, perhaps the user has hidden one of the observers
             */

            if (
                controllersInFutureQueue.length === 0 &&
                any(e => has(e, getState().paths))(outputIds) &&
                !controllerIsInExistingQueue
            ) {
                queuedObservers.push(outputIdAndProp);
            }
        });

        /*
         * record the set of output IDs that will eventually need to be
         * updated in a queue. not all of these requests will be fired in this
         * action
         */
        const newRequestQueue = queuedObservers.map(i => ({
            controllerId: i,
            status: 'loading',
            uid: uid(),
            requestTime: Date.now(),
        }));
        dispatch(setRequestQueue(concat(requestQueue, newRequestQueue)));

        const promises = [];
        for (let i = 0; i < queuedObservers.length; i++) {
            const outputIdAndProp = queuedObservers[i];
            const requestUid = newRequestQueue[i].uid;

            promises.push(
                updateOutput(
                    outputIdAndProp,
                    getState,
                    requestUid,
                    dispatch,
                    changedProps.map(prop => `${id}.${prop}`)
                )
            );
        }

        /* eslint-disable consistent-return */
        return Promise.all(promises);
        /* eslint-enable consistent-return */
    };
}

function updateOutput(
    outputIdAndProp,
    getState,
    requestUid,
    dispatch,
    changedPropIds
) {
    const {config, layout, graphs, dependenciesRequest, hooks} = getState();
    const {InputGraph} = graphs;

    const getThisRequestIndex = () => {
        const postRequestQueue = getState().requestQueue;
        const thisRequestIndex = findIndex(
            propEq('uid', requestUid),
            postRequestQueue
        );
        return thisRequestIndex;
    };

    const updateRequestQueue = (rejected, status) => {
        const postRequestQueue = getState().requestQueue;
        const thisRequestIndex = getThisRequestIndex();
        if (thisRequestIndex === -1) {
            // It was already pruned away
            return;
        }
        const updatedQueue = adjust(
            thisRequestIndex,
            mergeLeft({
                status: status,
                responseTime: Date.now(),
                rejected,
            }),
            postRequestQueue
        );
        // We don't need to store any requests before this one
        const thisControllerId =
            postRequestQueue[thisRequestIndex].controllerId;
        const prunedQueue = updatedQueue.filter((queueItem, index) => {
            return (
                queueItem.controllerId !== thisControllerId ||
                index >= thisRequestIndex
            );
        });

        dispatch(setRequestQueue(prunedQueue));
    };

    /*
     * Construct a payload of the input and state.
     * For example:
     * {
     *      inputs: [{'id': 'input1', 'property': 'new value'}],
     *      state: [{'id': 'state1', 'property': 'existing value'}]
     * }
     */

    // eslint-disable-next-line no-unused-vars
    const [outputComponentId, _] = outputIdAndProp.split('.');
    const payload = {
        output: outputIdAndProp,
        changedPropIds,
    };

    const {
        inputs,
        state,
        clientside_function,
    } = dependenciesRequest.content.find(
        dependency => dependency.output === outputIdAndProp
    );
    const validKeys = keys(getState().paths);

    payload.inputs = inputs.map(inputObject => {
        // Make sure the component id exists in the layout
        if (!includes(inputObject.id, validKeys)) {
            throw new ReferenceError(
                'An invalid input object was used in an ' +
                    '`Input` of a Dash callback. ' +
                    'The id of this object is `' +
                    inputObject.id +
                    '` and the property is `' +
                    inputObject.property +
                    '`. The list of ids in the current layout is ' +
                    '`[' +
                    validKeys.join(', ') +
                    ']`'
            );
        }
        const propLens = lensPath(
            concat(getState().paths[inputObject.id], [
                'props',
                inputObject.property,
            ])
        );
        return {
            id: inputObject.id,
            property: inputObject.property,
            value: view(propLens, layout),
        };
    });

    const inputsPropIds = inputs.map(p => `${p.id}.${p.property}`);

    payload.changedPropIds = changedPropIds.filter(p =>
        includes(p, inputsPropIds)
    );

    if (state.length > 0) {
        payload.state = state.map(stateObject => {
            // Make sure the component id exists in the layout
            if (!includes(stateObject.id, validKeys)) {
                throw new ReferenceError(
                    'An invalid input object was used in a ' +
                        '`State` object of a Dash callback. ' +
                        'The id of this object is `' +
                        stateObject.id +
                        '` and the property is `' +
                        stateObject.property +
                        '`. The list of ids in the current layout is ' +
                        '`[' +
                        validKeys.join(', ') +
                        ']`'
                );
            }
            const propLens = lensPath(
                concat(getState().paths[stateObject.id], [
                    'props',
                    stateObject.property,
                ])
            );
            return {
                id: stateObject.id,
                property: stateObject.property,
                value: view(propLens, layout),
            };
        });
    }

    function doUpdateProps(id, updatedProps) {
        const {layout, paths} = getState();
        const itempath = paths[id];
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

    // Clientside hook
    if (clientside_function) {
        let returnValue;
        try {
            returnValue = window.dash_clientside[clientside_function.namespace][
                clientside_function.function_name
            ](
                ...pluck('value', payload.inputs),
                ...(has('state', payload) ? pluck('value', payload.state) : [])
            );
        } catch (e) {
            /* eslint-disable no-console */
            console.error(
                `The following error occurred while executing ${clientside_function.namespace}.${clientside_function.function_name} ` +
                    `in order to update component "${payload.output}" ⋁⋁⋁`
            );
            console.error(e);
            /* eslint-enable no-console */

            /*
             * Update the request queue by treating an unsuccessful clientside
             * like a failed serverside response via same request queue
             * mechanism
             */

            updateRequestQueue(true, STATUS.CLIENTSIDE_ERROR);
            return;
        }

        // Returning promises isn't support atm
        if (type(returnValue) === 'Promise') {
            /* eslint-disable no-console */
            console.error(
                'The clientside function ' +
                    `${clientside_function.namespace}.${clientside_function.function_name} ` +
                    'returned a Promise instead of a value. Promises are not ' +
                    'supported in Dash clientside right now, but may be in the ' +
                    'future.'
            );
            /* eslint-enable no-console */
            updateRequestQueue(true, STATUS.CLIENTSIDE_ERROR);
            return;
        }

        function updateClientsideOutput(outputIdAndProp, outputValue) {
            const [outputId, outputProp] = outputIdAndProp.split('.');
            const updatedProps = {
                [outputProp]: outputValue,
            };

            /*
             * Update the request queue by treating a successful clientside
             * like a successful serverside response (200 status code)
             */
            updateRequestQueue(false, STATUS.OK);

            // Update the layout with the new result
            const appliedProps = doUpdateProps(outputId, updatedProps);

            /*
             * This output could itself be a serverside or clientside input
             * to another function
             */
            if (appliedProps) {
                dispatch(
                    notifyObservers({
                        id: outputId,
                        props: appliedProps,
                    })
                );
            }
        }

        if (isMultiOutputProp(payload.output)) {
            parseMultipleOutputs(payload.output).forEach((outputPropId, i) => {
                updateClientsideOutput(outputPropId, returnValue[i]);
            });
        } else {
            updateClientsideOutput(payload.output, returnValue);
        }

        /*
         * Note that unlike serverside updates, we're not handling
         * children as components right now, so we don't need to
         * crawl the computed result to check for nested components
         * or properties that might trigger other inputs.
         * In the future, we could handle this case.
         */
        return;
    }

    if (hooks.request_pre !== null) {
        hooks.request_pre(payload);
    }

    /* eslint-disable consistent-return */
    return fetch(
        `${urlBase(config)}_dash-update-component`,
        mergeDeepRight(config.fetch, {
            /* eslint-enable consistent-return */

            method: 'POST',
            headers: getCSRFHeader(),
            body: JSON.stringify(payload),
        })
    )
        .then(function handleResponse(res) {
            const isRejected = () => {
                const latestRequestIndex = findLastIndex(
                    propEq('controllerId', outputIdAndProp),
                    getState().requestQueue
                );
                /*
                 * Note that if the latest request is still `loading`
                 * or even if the latest request failed,
                 * we still reject this response in favor of waiting
                 * for the latest request to finish.
                 */
                const rejected = latestRequestIndex > getThisRequestIndex();
                return rejected;
            };

            if (res.status !== STATUS.OK) {
                // update the status of this request
                updateRequestQueue(true, res.status);

                /*
                 * This is a 204 response code, there's no content to process.
                 */
                if (res.status === STATUS.PREVENT_UPDATE) {
                    return;
                }

                /*
                 * eject into `catch` handler below to display error
                 * message in ui
                 */
                throw res;
            }

            /*
             * Check to see if another request has already come back
             * _after_ this one.
             * If so, ignore this request.
             */
            if (isRejected()) {
                updateRequestQueue(true, res.status);
                return;
            }

            res.json().then(function handleJson(data) {
                /*
                 * Even if the `res` was received in the correct order,
                 * the remainder of the response (res.json()) could happen
                 * at different rates causing the parsed responses to
                 * get out of order
                 */
                if (isRejected()) {
                    updateRequestQueue(true, res.status);
                    return;
                }

                updateRequestQueue(false, res.status);

                // Fire custom request_post hook if any
                if (hooks.request_post !== null) {
                    hooks.request_post(payload, data.response);
                }

                /*
                 * it's possible that this output item is no longer visible.
                 * for example, the could still be request running when
                 * the user switched the chapter
                 *
                 * if it's not visible, then ignore the rest of the updates
                 * to the store
                 */

                const multi = data.multi;

                const handleResponse = ([outputIdAndProp, props]) => {
                    // Backward compatibility
                    const pathKey = multi ? outputIdAndProp : outputComponentId;

                    const appliedProps = doUpdateProps(pathKey, props);
                    if (!appliedProps) {
                        return;
                    }

                    dispatch(
                        notifyObservers({
                            id: pathKey,
                            props: appliedProps,
                        })
                    );

                    /*
                     * If the response includes children, then we need to update our
                     * paths store.
                     * TODO - Do we need to wait for updateProps to finish?
                     */
                    if (has('children', appliedProps)) {
                        const newChildren = appliedProps.children;
                        dispatch(
                            computePaths({
                                subTree: newChildren,
                                startingPath: concat(
                                    getState().paths[pathKey],
                                    ['props', 'children']
                                ),
                            })
                        );

                        /*
                         * if children contains objects with IDs, then we
                         * need to dispatch a propChange for all of these
                         * new children components
                         */
                        if (
                            includes(type(newChildren), ['Array', 'Object']) &&
                            !isEmpty(newChildren)
                        ) {
                            /*
                             * TODO: We're just naively crawling
                             * the _entire_ layout to recompute the
                             * the dependency graphs.
                             * We don't need to do this - just need
                             * to compute the subtree
                             */
                            const newProps = {};
                            crawlLayout(newChildren, function appendIds(child) {
                                if (hasId(child)) {
                                    keys(child.props).forEach(childProp => {
                                        const componentIdAndProp = `${child.props.id}.${childProp}`;
                                        if (
                                            has(
                                                componentIdAndProp,
                                                InputGraph.nodes
                                            )
                                        ) {
                                            newProps[componentIdAndProp] = {
                                                id: child.props.id,
                                                props: {
                                                    [childProp]:
                                                        child.props[childProp],
                                                },
                                            };
                                        }
                                    });
                                }
                            });

                            /*
                             * Organize props by shared outputs so that we
                             * only make one request per output component
                             * (even if there are multiple inputs).
                             *
                             * For example, we might render 10 inputs that control
                             * a single output. If that is the case, we only want
                             * to make a single call, not 10 calls.
                             */

                            /*
                             * In some cases, the new item will be an output
                             * with its inputs already rendered (not rendered)
                             * as part of this update.
                             * For example, a tab with global controls that
                             * renders different content containers without any
                             * additional inputs.
                             *
                             * In that case, we'll call `updateOutput` with that output
                             * and just "pretend" that one if its inputs changed.
                             *
                             * If we ever add logic that informs the user on
                             * "which input changed", we'll have to account for this
                             * special case (no input changed?)
                             */

                            const outputIds = [];
                            keys(newProps).forEach(idAndProp => {
                                if (
                                    // It's an output
                                    InputGraph.dependenciesOf(idAndProp)
                                        .length === 0 &&
                                    /*
                                     * And none of its inputs are generated in this
                                     * request
                                     */
                                    intersection(
                                        InputGraph.dependantsOf(idAndProp),
                                        keys(newProps)
                                    ).length === 0
                                ) {
                                    outputIds.push(idAndProp);
                                    delete newProps[idAndProp];
                                }
                            });

                            // Dispatch updates to inputs
                            const reducedNodeIds = reduceInputIds(
                                keys(newProps),
                                InputGraph
                            );
                            const depOrder = InputGraph.overallOrder();
                            const sortedNewProps = sort(
                                (a, b) =>
                                    depOrder.indexOf(a.input) -
                                    depOrder.indexOf(b.input),
                                reducedNodeIds
                            );
                            sortedNewProps.forEach(function(inputOutput) {
                                const payload = newProps[inputOutput.input];
                                payload.excludedOutputs =
                                    inputOutput.excludedOutputs;
                                dispatch(notifyObservers(payload));
                            });

                            // Dispatch updates to lone outputs
                            outputIds.forEach(idAndProp => {
                                const requestUid = uid();
                                dispatch(
                                    setRequestQueue(
                                        append(
                                            {
                                                // TODO - Are there any implications of doing this??
                                                controllerId: null,
                                                status: 'loading',
                                                uid: requestUid,
                                                requestTime: Date.now(),
                                            },
                                            getState().requestQueue
                                        )
                                    )
                                );
                                updateOutput(
                                    idAndProp,

                                    getState,
                                    requestUid,
                                    dispatch,
                                    changedPropIds
                                );
                            });
                        }
                    }
                };
                if (multi) {
                    Object.entries(data.response).forEach(handleResponse);
                } else {
                    handleResponse([outputIdAndProp, data.response.props]);
                }
            });
        })
        .catch(err => {
            const message = `Callback error updating ${
                isMultiOutputProp(payload.output)
                    ? parseMultipleOutputs(payload.output).join(', ')
                    : payload.output
            }`;
            handleAsyncError(err, message, dispatch);
        });
}

export function handleAsyncError(err, message, dispatch) {
    // Handle html error responses
    const errText =
        err && typeof err.text === 'function'
            ? err.text()
            : Promise.resolve(err);

    errText.then(text => {
        dispatch(
            onError({
                type: 'backEnd',
                error: {
                    message,
                    html: text,
                },
            })
        );
    });
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
