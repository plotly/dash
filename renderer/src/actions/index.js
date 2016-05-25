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
export const updateDependants = function(payload) {
    return function (dispatch, getState) {
        const {
            layout,
            dependencyGraph,
            paths,
            requestQueue
        } = getState();

        // Grab the ids of any components that depend on this component
        let dependantIds = dependencyGraph.dependantsOf(payload.id);

        // order the dependant ids
        const depOrder = dependencyGraph.overallOrder();
        dependantIds = R.sort(
            (a, b) => depOrder.indexOf(a) - depOrder.indexOf(b),
            dependantIds
        );

        // record the set of requests in the queue
        dispatch(setRequestQueue(R.union(dependantIds, requestQueue)));

        // update each dependant component
        for (let i = 0; i < dependantIds.length; i++) {
            const dependantId = dependantIds[i];
            const dependantComponent = layout.getIn(paths[dependantId]);

            /*
             * before we make the POST, check that none of it's dependencies
             * are already in the queue. if they are in the queue, then don't update.
             * when each dependency updates, it'll dispatch it's own `updateDependants`
             * action which will allow this component to update.
             */
            if (R.intersection(
                    getState().requestQueue,
                    dependencyGraph.dependenciesOf(dependantId)
                ).length === 0) {

                // construct a payload of the props of all of the dependencies
                const payload = dependantComponent.get('dependencies').reduce(
                    (r, id) => {
                        r[id] = layout.getIn(R.append('props', paths[id])).toJS();
                        return r;
                    }, {target: dependantId}
                );

                /* eslint-disable no-console */

                // make the /POST
                // xhr.POST(/update-component) ...
                console.warn('POST /update-component', JSON.stringify(payload, null, 2));

                // mimic async POST request behaviour with setTimeout
                setTimeout(() => {
                    // clear this item from the request queue
                    console.warn(`RESPONSE ${dependantId}`);
                    dispatch(setRequestQueue(
                        R.reject(
                            id => id === dependantId,
                            // in an async loop so grab the state again
                            getState().requestQueue)
                        )
                    );

                    // and update the props of the component
                    const dependantUpdatePayload = {
                        itempath: paths[dependantId],
                        // new props from the server, just hard coded here
                        props: {value: 1000*Math.random()}
                    };
                    dispatch(updateProps(dependantUpdatePayload));

                    // and now update *this* component's dependencies
                    dependantUpdatePayload.id = dependantId;
                    dispatch(updateDependants(dependantUpdatePayload));
                }, 10000*Math.random());

                /* eslint-enable no-console */

            }

        }
    }
}
