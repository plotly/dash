import R from 'ramda';
import { createAction } from 'redux-actions';

export const ACTIONS = (action) => {
    const actionList = {
        ON_PROP_CHANGE: 'ON_PROP_CHANGE'
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
        let dependentIds = dependencyGraph.dependantsOf(payload.id);

        // order the dependent ids
        const depOrder = dependencyGraph.overallOrder();
        dependentIds = R.sort(
            (a, b) => depOrder.indexOf(a) - depOrder.indexOf(b),
            dependentIds
        );

        // record the set of requests in the queue
        dispatch(setRequestQueue(R.union(dependentIds, requestQueue)));

        for (let i = 0; i < dependentIds.length; i++) {
            const dependentId = dependentIds[i];
            const dependentComponent = layout.getIn(paths[dependentId]);

            const payload = dependentComponent.get('dependencies').reduce(
                (r, id) => {
                    r[id] = layout.getIn(R.append('props', paths[id])).toJS();
                    return r;
                }, {target: dependentId}
            );

            /*
             * before we make the POST, check that some recursive call hasn't
             * already cleared this request from the queue
             */
            if (getState().requestQueue.indexOf(dependentId) > -1) {

                // make the /POST
                // xhr.POST(/update-component) ...
                console.warn('POST /update-component', JSON.stringify(payload, null, 2));

                // clear this item from the request queue
                dispatch(setRequestQueue(
                    R.reject(
                        id => id === dependentId,
                        // in an async loop so grab the state again
                        getState().requestQueue)
                    )
                );

                // and update the props of the component
                const dependentUpdatePayload = {
                    id: dependentId,
                    itempath: paths[dependentId],
                    // new props from the server, just hard coded here
                    value: 1000*Math.random()
                };
                dispatch(updateProps(dependentUpdatePayload));

                // and now update *this* component's dependencies
                dispatch(updateDependants(dependentUpdatePayload));

            }

        }
    }
}
