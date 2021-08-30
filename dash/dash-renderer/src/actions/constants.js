const actionList = {
    ON_PROP_CHANGE: 1,
    SET_REQUEST_QUEUE: 1,
    SET_GRAPHS: 1,
    SET_PATHS: 1,
    SET_LAYOUT: 1,
    SET_APP_LIFECYCLE: 1,
    SET_CONFIG: 1,
    SET_CONFIG_NO_REFRESH: 2,
    ON_ERROR: 1,
    SET_HOOKS: 1
};

export const getAction = action => {
    if (actionList[action]) {
        return action;
    }
    throw new Error(`${action} is not defined.`);
};

export const MAX_AUTH_RETRIES = 1;
