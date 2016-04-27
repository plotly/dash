import { createAction } from 'redux-actions';

export const ACTIONS = (action) => {
    const actionList = {
        ON_PROP_CHANGE: 'ON_PROP_CHANGE'
    };
    if (actionList[action]) return actionList[action];
    else throw new Exception(`${action} is not defined.`)
};

export const updateProps = createAction(ACTIONS('ON_PROP_CHANGE'));
