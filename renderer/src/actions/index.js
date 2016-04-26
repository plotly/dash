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

