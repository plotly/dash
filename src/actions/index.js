/* eslint-disable no-console */
import R, {view, lensPath, merge} from 'ramda';
import { createAction } from 'redux-actions';

export const ACTIONS = (action) => {
    const actionList = {
        ON_PROP_CHANGE: 'ON_PROP_CHANGE',
        SET_REQUEST_QUEUE: 'SET_REQUEST_QUEUE',
        SET_LAYOUT: 'SET_LAYOUT',
        COMPUTE_GRAPH: 'COMPUTE_GRAPH',
        COMPUTE_PATHS: 'COMPUTE_PATHS'
    };
    if (actionList[action]) return actionList[action];
    else throw new Error(`${action} is not defined.`)
};

export const updateProps = createAction(ACTIONS('ON_PROP_CHANGE'));
export const setRequestQueue = createAction(ACTIONS('SET_REQUEST_QUEUE'));
const setLayout = createAction(ACTIONS('SET_LAYOUT'));
const computeGraph = createAction(ACTIONS('COMPUTE_GRAPH'));
const computePaths = createAction(ACTIONS('COMPUTE_PATHS'));

export const initialize = function() {
    return function (dispatch) {
        console.warn('initializing GET.');
        fetch('/initialize', {method: 'GET'})
        .then(res => res.json().then(layout => {
            // TODO: error handling
            console.warn(JSON.stringify(layout, null, 2));
            dispatch(setLayout(layout));
            dispatch(computeGraph(layout));
            dispatch(computePaths(layout))
        }));
    }
}

// TODO: Consider moving side effects to reducers via https://github.com/gregwebs/redux-side-effect
export const notifyObservers = function(payload) {
    return function (dispatch, getState) {
        const {
            layout,
            dependencyGraph,
            paths,
            requestQueue
        } = getState();

        // debugger;

        // Grab the ids of any components that depend on this component
        let observerIds = dependencyGraph.dependantsOf(payload.id);

        // order the observer ids
        const depOrder = dependencyGraph.overallOrder();
        observerIds = R.sort(
            (a, b) => depOrder.indexOf(a) - depOrder.indexOf(b),
            observerIds
        );

        // record the set of requests in the queue
        dispatch(setRequestQueue(R.union(observerIds, requestQueue)));

        // update each observer
        for (let i = 0; i < observerIds.length; i++) {
            const observerId = observerIds[i];
            const observerComponent = view(lensPath(paths[observerId]), layout);

            /*
             * before we make the POST, check that none of its dependencies
             * are already in the queue. if they are in the queue, then don't update.
             * when each dependency updates, it'll dispatch its own `notifyObservers`
             * action which will allow this component to update.
             */

            const dependenciesInQueue = R.intersection(
                getState().requestQueue,
                dependencyGraph.dependenciesOf(observerId)
            );
            if (dependenciesInQueue.length !== 0) {

                console.warn(`SKIP updating ${observerId}, waiting for ${dependenciesInQueue} to update.`);

            } else {

                /*
                 * Construct a payload of the props of all of the dependencies
                 * (controller components of this observer component).
                 */
                const controllers = observerComponent.dependencies.reduce(
                    (r, id) => {
                        r[id] = view(lensPath(paths[id]), layout);
                        return r;
                    }, {}
                );
                const body = {
                    target: view(lensPath(paths[observerId]), layout),
                    parents: controllers
                }

                /* eslint-disable no-console */

                // make the /POST
                console.warn(`POST: ${observerId}`);

                fetch('/interceptor', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(body)
                }).then(response => response.json().then(function handleResponse(data) {

                    // clear this item from the request queue
                    console.warn(
                        `RESPONSE: ${observerId}`,
//                        JSON.stringify(data, null, 2)
                    );
                    dispatch(setRequestQueue(
                        R.reject(
                            id => id === observerId,
                            // in an async loop so grab the state again
                            getState().requestQueue
                        )
                    ));

                    // and update the props of the component
                    const observerUpdatePayload = {
                        itempath: paths[observerId],
                        // new props from the server
                        props: merge(data.response.props, {content: data.response.children})
                    };
                    dispatch(updateProps(observerUpdatePayload));

                    // and now update *this* component's dependencies
                    observerUpdatePayload.id = observerId;
                    dispatch(notifyObservers(observerUpdatePayload));

                }));

            }
        }
    }
}
