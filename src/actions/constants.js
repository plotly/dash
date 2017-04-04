export const ACTIONS = (action) => {
    const actionList = {
        ON_PROP_CHANGE: 'ON_PROP_CHANGE',
        SET_REQUEST_QUEUE: 'SET_REQUEST_QUEUE',
        COMPUTE_GRAPHS: 'COMPUTE_GRAPHS',
        COMPUTE_PATHS: 'COMPUTE_PATHS',
        SET_LAYOUT: 'SET_LAYOUT',
        SET_APP_LIFECYCLE: 'SET_APP_LIFECYCLE'
    };
    if (actionList[action]) return actionList[action];
    else throw new Error(`${action} is not defined.`)
};
