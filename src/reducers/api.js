import {assoc, assocPath, merge} from 'ramda';

function createApiReducer(store) {
    return function ApiReducer(state = {}, action) {
        let newState = state;
        if (action.type === store) {
            const {payload} = action;
            if (Array.isArray(payload.id)) {
                newState = assocPath(
                    payload.id,
                    {
                        status: payload.status,
                        content: payload.content,
                    },
                    state
                );
            } else if (payload.id) {
                newState = assoc(
                    payload.id,
                    {
                        status: payload.status,
                        content: payload.content,
                    },
                    state
                );
            } else {
                newState = merge(state, {
                    status: payload.status,
                    content: payload.content,
                });
            }
        }
        return newState;
    };
}

export const dependenciesRequest = createApiReducer('dependenciesRequest');
export const layoutRequest = createApiReducer('layoutRequest');
export const reloadRequest = createApiReducer('reloadRequest');
export const loginRequest = createApiReducer('loginRequest');
