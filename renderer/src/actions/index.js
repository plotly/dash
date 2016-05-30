import R from 'ramda';
import { createAction } from 'redux-actions';

export const ACTIONS = (action) => {
    const actionList = {
        ON_PROP_CHANGE: 'ON_PROP_CHANGE',
        SET_REQUEST_QUEUE: 'SET_REQUEST_QUEUE'
    };
    if (actionList[action]) return actionList[action];
    else throw new Error(`${action} is not defined.`)
};

export const updateProps = createAction(ACTIONS('ON_PROP_CHANGE'));
export const setRequestQueue = createAction(ACTIONS('SET_REQUEST_QUEUE'));

// TODO: make the actual POST
export const notifyObservers = function(payload) {
    return function (dispatch, getState) {
        const {
            layout,
            dependencyGraph,
            paths,
            requestQueue
        } = getState();

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
            const observerComponent = layout.getIn(paths[observerId]);

            /*
             * before we make the POST, check that none of it's dependencies
             * are already in the queue. if they are in the queue, then don't update.
             * when each dependency updates, it'll dispatch it's own `notifyObservers`
             * action which will allow this component to update.
             */
            if (R.intersection(
                    // TODO Can just use `requestQueue`.
                    getState().requestQueue,
                    dependencyGraph.dependenciesOf(observerId)
                ).length === 0) {

                /*
                 * Construct a payload of the props of all of the dependencies
                 * (controller components of this observer component).
                 */
                const payload = observerComponent.get('dependencies').reduce(
                    (r, id) => {
                        r[id] = layout.getIn(R.append('props', paths[id])).toJS();
                        return r;
                    }, {target: observerId}
                );

                /* eslint-disable no-console */

                // make the /POST
                // xhr.POST(/update-component) ...
                console.warn('POST /update-component', JSON.stringify(payload, null, 2));

                // mimic async POST request behaviour with setTimeout
                setTimeout(() => {
                    // clear this item from the request queue
                    console.warn(`RESPONSE ${observerId}`);
                    dispatch(setRequestQueue(
                        R.reject(
                            id => id === observerId,
                            // in an async loop so grab the state again
                            getState().requestQueue)
                        )
                    );

                    // and update the props of the component
                    const observerUpdatePayload = {
                        itempath: paths[observerId],
                        // new props from the server, just hard coded here
                        props: {value: 1000*Math.random()}
                    };
                    dispatch(updateProps(observerUpdatePayload));

                    // and now update *this* component's dependencies
                    observerUpdatePayload.id = observerId;
                    dispatch(notifyObservers(observerUpdatePayload));
                }, 10000*Math.random());

                /* eslint-enable no-console */

            }
        }
    }
}
