import {
    concat,
    contains,
    has,
    intersection,
    isEmpty,
    isNil,
    filter,
    keys,
    lensPath,
    merge,
    omit,
    pick,
    reject,
    sort,
    type,
    union,
    view
} from 'ramda';
import {createAction} from 'redux-actions';
import {crawlLayout, hasId} from '../reducers/utils';

export const ACTIONS = (action) => {
    const actionList = {
        ON_PROP_CHANGE: 'ON_PROP_CHANGE',
        SET_REQUEST_QUEUE: 'SET_REQUEST_QUEUE',
        SET_LAYOUT: 'SET_LAYOUT',
        COMPUTE_GRAPHS: 'COMPUTE_GRAPHS',
        COMPUTE_PATHS: 'COMPUTE_PATHS'
    };
    if (actionList[action]) return actionList[action];
    else throw new Error(`${action} is not defined.`)
};

export const updateProps = createAction(ACTIONS('ON_PROP_CHANGE'));
export const setRequestQueue = createAction(ACTIONS('SET_REQUEST_QUEUE'));
const setLayout = createAction(ACTIONS('SET_LAYOUT'));
const computeGraphs = createAction(ACTIONS('COMPUTE_GRAPHS'));
const computePaths = createAction(ACTIONS('COMPUTE_PATHS'));

export const initialize = function() {
    return function (dispatch, getState) {
        // TODO - Use whatwg-fetch
        fetch('/initialize', {method: 'GET'}) /* global fetch: true */
        .then(res => res.json().then(layout => {
            // TODO: error handling
            dispatch(setLayout(layout));
            dispatch(computePaths({subTree: layout, startingPath: []}));
        })).then(function() {
            fetch('/dependencies', {method: 'GET'})
            .then(res => res.json().then(dependencies => {
                dispatch(computeGraphs(dependencies));
                /*
                 * Fire an initial propChange event for each of the controllers
                 * so that the observer leaves can update
                 */
                // TODO - Use thunk instead of setTimeout
                setTimeout(function(){
                    const {graphs} = getState();
                    const {EventGraph} = graphs;
                    EventGraph.overallOrder().forEach(nodeId => {
                        // Only fire updates for the visible controllers
                        if (has(nodeId, getState().paths)) {
                            dispatch(notifyObservers({
                                event: 'propChange', id: nodeId
                            }));
                        }

                    });
                }, 50)
            }));
        });
    }
}

/*
 * TODO: Consider moving side effects to reducers via
 * https://github.com/gregwebs/redux-side-effect
 */
export const notifyObservers = function(payload) {
    return function (dispatch, getState) {
        const {
            event,
            id
        } = payload

        const {
            layout,
            graphs,
            paths,
            requestQueue
        } = getState();
        const {EventGraph, StateGraph} = graphs;

        /*
         * Each observer may depend on a different set of events.
         * Filter away the observers that are listening to different events.
         */
        const observersAndEventSubscriptions = EventGraph.getNodeData(id);
        let eventObservers = keys(filter(function filterObservers(observerEventSubscriptions) {
            return contains(event, observerEventSubscriptions);
        }, observersAndEventSubscriptions));

        /*
         * If no components have subscribed to these events,
         * then we have no one else to tell about it.
         */
        if (isEmpty(eventObservers)) {
            return;
        }

        /*
         * There may be several components that depend on this event.
         * And some components may depend on other components before
         * updating. Get this update order straightened out.
         */
        const depOrder = EventGraph.overallOrder();
        eventObservers = sort(
            (a, b) => depOrder.indexOf(a) - depOrder.indexOf(b),
            eventObservers
        );

        // record the set of requests in the queue
        dispatch(setRequestQueue(union(eventObservers, requestQueue)));

        // update each observer
        for (let i = 0; i < eventObservers.length; i++) {
            const eventObserverId = eventObservers[i];

            /*
             * before we make the POST, check that none of its event dependencies
             * are already in the queue. if they are in the queue, then don't update.
             * when each dependency updates, it'll dispatch its own `notifyObservers`
             * action which will allow this component to update.
             *
             * for example, if A updates B and C (A -> [B, C]) and B updates C
             * (B -> C), then when A updates, we can update B but not C until
             * B is done updating. in this scenario, B is before C from the
             * overallOrder, so it'll get set in the requestQueue before C.
             */
            const dependenciesInQueue = intersection(
                getState().requestQueue,
                EventGraph.dependenciesOf(eventObserverId)
            );

            if (dependenciesInQueue.length !== 0) {
                continue;
            }

            /*
             * also check that this observer is actually in the current
             * component tree.
             * observers don't actually need to be rendered at the moment
             * of a controller change.
             * for example, perhaps the user has hidden one of the observers
             */
            if (!has(eventObserverId, getState().paths)) {
                continue;
            }

            /*
             * Construct a payload of the subscribed state
             * For example, if graph depends on `input1` value and style
             * and `input2` value, the payload would look like:
             * {input1: {value: ..., style: ...,}, input2: ...}
             */
            let state = {};
            StateGraph.dependenciesOf(eventObserverId).forEach(function reduceState(controllerId) {
                const observedProps = StateGraph.getNodeData(controllerId)[eventObserverId];
                /*
                 * StateGraph.dependenciesOf doesn't just return neighbors,
                 * it also returns grandparents and other non-direct-neighbor
                 * nodes. Dang!
                 * If a controller doesn't have this eventObserverId in it's
                 * node data, then it's not an immediate dependency.
                 */
                if (isEmpty(observedProps) || isNil(observedProps)) {
                    return;
                }
                state[controllerId] = {};

                const propLens = lensPath(concat(paths[controllerId], ['props']));
                const props = view(propLens, layout);
                // TODO - Is * and omit the right pattern?
                if (observedProps[0] === '*') {
                    state[controllerId] = omit(['content'], props);
                } else {
                    state[controllerId] = pick(observedProps, props);
                }
            });

            const body = {id: eventObserverId, state};

            // make the /POST
            fetch('/interceptor', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            }).then(response => response.json().then(function handleResponse(data) {
                // clear this item from the request queue
                dispatch(setRequestQueue(
                    reject(
                        id => id === eventObserverId,
                        // in an async loop so grab the state again
                        getState().requestQueue
                    )
                ));

                // and update the props of the component
                const observerUpdatePayload = {
                    itempath: paths[eventObserverId],
                    // new props from the server
                    props: merge(data.response.props, {content: data.response.children})
                };
                dispatch(updateProps(observerUpdatePayload));


                // fire an event that the props have changed
                // TODO - Need to wait for updateProps to finish?
                dispatch(notifyObservers({event: 'propChange', id: eventObserverId}));

                /*
                 * If the response includes content which includes or
                 * or removes items with IDs, then we need to update our
                 * paths store.
                 * TODO - Do we need to wait for updateProps to finish?
                 */
                if (contains(
                        type(observerUpdatePayload.props.content),
                        ['Array', 'Object']
                    ) && !isEmpty(observerUpdatePayload.props.content)) {

                    dispatch(computePaths({
                        subTree: observerUpdatePayload.props.content,
                        startingPath: concat(
                            getState().paths[eventObserverId],
                            ['props', 'content']
                        )
                    }));

                    /*
                     * And then we need to dispatch
                     * an initialization propChange for all
                     *  of _these_ components!
                     * TODO: We're just naively crawling
                     * the _entire_ layout to recompute the
                     * the dependency graphs.
                     * We don't need to do this - just need
                     * to compute the subtree
                     */
                    const newIds = [];
                    crawlLayout(
                        observerUpdatePayload.props.content,
                        function appendIds(child) {
                            if (hasId(child) &&
                                /*
                                 * Not all nodes that have IDs
                                 * are necessarily bound to events
                                 * TODO - Are we making that assumption anywhere else?
                                 */
                                has(child.props.id, EventGraph.nodes)
                            ) {
                                newIds.push(child.props.id);
                            }
                        }
                    );

                    // TODO - We might need to reset the
                    // request queue here.
                    const depOrder = EventGraph.overallOrder();
                    const sortedIds = sort((a, b) => depOrder.indexOf(a) - depOrder.indexOf(b),
                        newIds
                    )
                    sortedIds.forEach(function(newId) {
                        dispatch(notifyObservers({
                            event: 'propChange', id: newId
                        }));
                    });

                }


            }));

        }
    }
}
