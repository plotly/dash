/* global fetch:true, window:true, Promise:true */
import {
    concat,
    contains,
    has,
    intersection,
    isEmpty,
    keys,
    lensPath,
    pluck,
    reject,
    sort,
    type,
    union,
    view
} from 'ramda';
import {createAction} from 'redux-actions';
import {crawlLayout, hasId} from '../reducers/utils';
import {APP_STATES} from '../reducers/constants';
import {ACTIONS} from './constants';

export const updateProps = createAction(ACTIONS('ON_PROP_CHANGE'));
export const setRequestQueue = createAction(ACTIONS('SET_REQUEST_QUEUE'));
export const computeGraphs = createAction(ACTIONS('COMPUTE_GRAPHS'));
export const computePaths = createAction(ACTIONS('COMPUTE_PATHS'));
export const setLayout = createAction(ACTIONS('SET_LAYOUT'));
export const setAppLifecycle = createAction(ACTIONS('SET_APP_LIFECYCLE'));

export const hydrateInitialOutputs = function() {
    return function (dispatch, getState) {
        const {routesRequest} = getState();
        if (!isEmpty(routesRequest.content) &&
            contains(
                window.location.pathname,
                pluck('pathname', routesRequest.content)
            )
        ) {
            loadStateFromRoute()(dispatch, getState);
        } else {
            triggerDefaultState(dispatch, getState);
        }
        dispatch(setAppLifecycle(APP_STATES('HYDRATED')));
    }
};

export function loadStateFromRoute() {
    return (dispatch, getState) => {
        const {routesRequest} = getState();
        const routes = routesRequest.content;
        const route = routes.find(route => (
            route.pathname === window.location.pathname
        ));
        const initialState = route.state;
        loadSavedState(initialState)(dispatch, getState)
    }
}

function loadSavedState(initialControls) {
    return (dispatch, getState) => {
        function recursivelyTriggerInputs(skipTheseInputs) {
            const {
                promises,
                visibleInputsThatWereTriggered
            } = loadSavedStateAndTriggerVisibleInputs(
                dispatch, getState, skipTheseInputs, initialControls
            );
            if (promises.length === 0) {
                return;
            } else {
                Promise.all(promises).then(function() {
                    recursivelyTriggerInputs(union(
                        skipTheseInputs,
                        visibleInputsThatWereTriggered
                    ));
                });
            }
        }

        recursivelyTriggerInputs([]);
    }
}

function loadSavedStateAndTriggerVisibleInputs(dispatch, getState, skipTheseInputs, initialControls) {
    const updatedInputs = [];
    const {paths} = getState();

    keys(initialControls).forEach((nodeId) => {
        const [componentId, componentProp] = nodeId.split('.');

        /*
         * Don't update invisible inputs - they'll become visible
         * as a result of a separate input on a later cycle
         */
        if (!(has(componentId, paths))) {
            return;
        }

        // Some input nodes have already been updated in a previous cycle
        if (contains(nodeId, skipTheseInputs)) {
            return;
        }

        const payload = {
            itempath: paths[componentId],
            props: {[componentProp]: initialControls[nodeId]}
        }
        dispatch(updateProps(payload));
        updatedInputs.push(nodeId);
    });

    const {graphs} = getState();
    const InputGraph = graphs.InputGraph
    const triggeredInputs = [];
    const promises = [];

    // Trigger an update for each of the output nodes
    keys(InputGraph.nodes).forEach(nodeId => {
        if (InputGraph.dependenciesOf(nodeId).length === 0) {
            /*
             * If the output has more than one input, then just
             * trigger an update on one of the updates.
             * All of the inputs are already updated, so we don't
             * need to trigger it more than once.
             */
            const anInputNode = InputGraph.dependantsOf(nodeId)[0];

            /*
             * It's possible that this output has already been updated
             * by a different output that shared the same input
             */
            if (contains(anInputNode, triggeredInputs)) {
                return;
            }

            const [anInputId, anInputProp] = anInputNode.split('.');

            /*
             * Don't update invisible inputs - they'll become visible
             * as a result of a separate input on a later cycle
             */
            if (!(has(anInputId, getState().paths))) {
                return;
            }

            // Some input nodes have already been updated in a previous cycle
            if (contains(anInputNode, skipTheseInputs)) {
                return;
            }

            const propLens = lensPath(
                concat(getState().paths[anInputId],
                ['props', anInputProp]
            ));
            const propValue = view(
                propLens,
                getState().layout
            );

            /*
             * We only want to update the nodes that aren't inputs -
             * the input nodes have already been updated by the
             * setProps action above
             * (since the value of the inputs was saved)
             */
             const dontUpdateInputObservers = true;

            promises.push(dispatch(notifyObservers({
                id: anInputId,
                props: {
                    [anInputProp]: propValue
                },
                dontUpdateInputObservers
            })));
            triggeredInputs.push(anInputNode);
        }
    });

    return {
        promises,

        // TODO - Do I really need to take the union?
        // Isn't triggeredInputs just a subset of updatedInputs?
        visibleInputsThatWereTriggered: union(triggeredInputs, updatedInputs)
    };
}

function triggerDefaultState(dispatch, getState) {
    const {graphs} = getState();
    const {InputGraph} = graphs;
    const allNodes = InputGraph.overallOrder();
    allNodes.reverse();
    allNodes.forEach(nodeId => {
        const [componentId, componentProp] = nodeId.split('.');

        /*
         * Filter out the outputs,
         * inputs that aren't leaves,
         * and the invisible inputs
         */
        if (InputGraph.dependenciesOf(nodeId).length > 0 &&
            InputGraph.dependantsOf(nodeId).length == 0 &&
            has(componentId, getState().paths)
        ) {

            // Get the initial property
            const propLens = lensPath(
                concat(getState().paths[componentId],
                ['props', componentProp]
            ));
            const propValue = view(
                propLens,
                getState().layout
            );

            dispatch(notifyObservers({
                id: componentId,
                props: {[componentProp]: propValue}
            }));

        }
    });
}

export function redo() {
    return function (dispatch, getState) {
        const history = getState().history;
        dispatch(createAction('REDO')());
        const next = history.future[0];

        // Update props
        dispatch(createAction('REDO_PROP_CHANGE')({
            itempath: getState().paths[next.id],
            props: next.props
        }));

        // Notify observers
        dispatch(notifyObservers({
            id: next.id,
            props: next.props
        }));
    }
}


export function undo() {
    return function (dispatch, getState) {
        const history = getState().history;
        dispatch(createAction('UNDO')());
        const previous = history.past[history.past.length - 1];

        // Update props
        dispatch(createAction('UNDO_PROP_CHANGE')({
            itempath: getState().paths[previous.id],
            props: previous.props
        }));

        // Notify observers
        dispatch(notifyObservers({
            id: previous.id,
            props: previous.props
        }));
    }
}




export const notifyObservers = function(payload) {
    return function (dispatch, getState) {
        const {
            id,
            event,
            props
        } = payload

        const dontUpdateInputObservers = (
            has('dontUpdateInputObservers', payload) ?
            payload.dontUpdateInputObservers : false
        );

        const {
            layout,
            graphs,
            paths,
            requestQueue,
            dependenciesRequest
        } = getState();
        const {EventGraph, InputGraph} = graphs;

        /*
         * Figure out all of the output id's that depend on this
         * event or input.
         * This includes id's that are direct children as well as
         * grandchildren.
         * grandchildren will get filtered out in a later stage.
         */
        let outputObservers;
        if (event) {
            outputObservers = EventGraph.dependenciesOf(`${id}.${event}`);
        } else {
            const changedProps = keys(props);
            outputObservers = [];
            changedProps.forEach(propName => {
                InputGraph.dependenciesOf(`${id}.${propName}`).forEach(outputId => {
                    if (dontUpdateInputObservers) {
                        // Only update output elements
                        if (InputGraph.dependenciesOf(outputId).length === 0) {
                            outputObservers.push(outputId);
                        }
                    } else {
                        outputObservers.push(outputId);
                    }

                });
            });
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
            const outputComponentId = outputIdAndProp.split('.')[0];
            /*
             * before we make the POST, check that none of its input
             * dependencies are already in the queue.
             * if they are in the queue, then don't update.
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

            const controllersInQueue = intersection(
                queuedObservers,

                /*
                 * if the output just listens to events, then it won't be in
                 * the InputGraph
                 */
                InputGraph.hasNode(outputIdAndProp) ?
                InputGraph.dependantsOf(outputIdAndProp) : []
            );

            /*
             * also check that this observer is actually in the current
             * component tree.
             * observers don't actually need to be rendered at the moment
             * of a controller change.
             * for example, perhaps the user has hidden one of the observers
             */
             if (
                 (controllersInQueue.length === 0) &&
                 (has(outputComponentId, getState().paths))
             ) {
                 queuedObservers.push(outputIdAndProp)
             }
        });
        /*
         * record the set of output IDs that will eventually need to be
         * updated in a queue. not all of these requests will be fired in this
         * action
         */
        dispatch(setRequestQueue(union(queuedObservers, requestQueue)));
        const promises = [];
        for (let i = 0; i < queuedObservers.length; i++) {
            const outputIdAndProp = queuedObservers[i];
            const [outputComponentId, outputProp] = outputIdAndProp.split('.');

            /*
             * Construct a payload of the input, state, and event.
             * For example:
             * If the input triggered this update, then:
             * {
             *      inputs: [{'id': 'input1', 'property': 'new value'}],
             *      state: [{'id': 'state1', 'property': 'existing value'}]
             * }
             *
             * If an event triggered this udpate, then:
             * {
             *      state: [{'id': 'state1', 'property': 'existing value'}],
             *      event: {'id': 'graph', 'event': 'click'}
             * }
             *
             */
             const payload = {
                 output: {id: outputComponentId, property: outputProp}
             };

             if (event) {
                 payload.event = event;
             }

            const {inputs, state} = dependenciesRequest.content.find(
                dependency => (
                    dependency.output.id === outputComponentId &&
                    dependency.output.property === outputProp
                )
            )
            if (inputs.length > 0) {
                payload.inputs = inputs.map(inputObject => {
                    const propLens = lensPath(
                        concat(paths[inputObject.id],
                        ['props', inputObject.property]
                    ));
                    return {
                        id: inputObject.id,
                        property: inputObject.property,
                        value: view(propLens, layout)
                    };
                });
            }
            if (state.length > 0) {
                payload.state = state.map(stateObject => {
                    const propLens = lensPath(
                        concat(paths[stateObject.id],
                        ['props', stateObject.property]
                    ));
                    return {
                        id: stateObject.id,
                        property: stateObject.property,
                        value: view(propLens, layout)
                    };
                });
            }



            promises.push(fetch('/update-component', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            }).then(response => response.json().then(function handleResponse(data) {
                // clear this item from the request queue
                dispatch(setRequestQueue(
                    reject(
                        id => id === outputIdAndProp,
                        getState().requestQueue
                    )
                ));

                /*
                 * it's possible that this output item is no longer visible.
                 * for example, the could still be request running when
                 * the user switched the chapter
                 *
                 * if it's not visible, then ignore the rest of the updates
                 * to the store
                 */
                if (!has(outputComponentId, getState().paths)) {
                    return;
                }

                // and update the props of the component
                const observerUpdatePayload = {
                    itempath: getState().paths[outputComponentId],
                    // new prop from the server
                    props: data.response.props,
                    source: 'response'
                };
                dispatch(updateProps(observerUpdatePayload));

                dispatch(notifyObservers({
                    id: outputComponentId,
                    props: data.response.props
                }));

                /*
                 * If the response includes content, then we need to update our
                 * paths store.
                 * TODO - Do we need to wait for updateProps to finish?
                 */
                if (has('content', observerUpdatePayload.props)) {

                    dispatch(computePaths({
                        subTree: observerUpdatePayload.props.content,
                        startingPath: concat(
                            getState().paths[outputComponentId],
                            ['props', 'content']
                        )
                    }));

                    /*
                     * if content contains objects with IDs, then we
                     * need to dispatch a propChange for all of these
                     * new children components
                     */
                    if (contains(
                            type(observerUpdatePayload.props.content),
                            ['Array', 'Object']
                        ) && !isEmpty(observerUpdatePayload.props.content)
                    ) {
                        /*
                         * TODO: We're just naively crawling
                         * the _entire_ layout to recompute the
                         * the dependency graphs.
                         * We don't need to do this - just need
                         * to compute the subtree
                         */
                        const newProps = [];
                        crawlLayout(
                            observerUpdatePayload.props.content,
                            function appendIds(child) {
                                if (hasId(child)) {
                                    keys(child.props).forEach(childProp => {
                                        const inputId = (
                                            `${child.props.id}.${childProp}`
                                        );
                                        if (has(inputId, InputGraph.nodes)) {
                                            newProps.push({
                                                id: child.props.id,
                                                props: {
                                                    [childProp]: child.props[childProp]
                                                },
                                                dontUpdateInputObservers
                                            });
                                        }
                                    })
                                }
                            }
                        );

                        const depOrder = InputGraph.overallOrder();
                        const sortedNewProps = sort((a, b) =>
                            depOrder.indexOf(a.id) - depOrder.indexOf(b.id),
                            newProps
                        )
                        if (!dontUpdateInputObservers) {
                            sortedNewProps.forEach(function(propUpdate) {
                                dispatch(notifyObservers(propUpdate));
                            });
                        }
                    }


                }

            })));

        }

        return Promise.all(promises);
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
        if (InputGraph.dependenciesOf(nodeId).length > 0 &&
            has(componentId, paths)
        ) {
            // Get the property
            const propLens = lensPath(
                concat(paths[componentId],
                ['props', componentProp]
            ));
            const propValue = view(
                propLens,
                layout
            );
            savedState[nodeId] = propValue;
        }
    });

    return savedState;

}
