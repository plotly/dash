import {assoc, assocPath, mergeRight} from 'ramda';

export default function createApiReducer(store) {
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
                newState = mergeRight(state, {
                    status: payload.status,
                    content: payload.content,
                });
            }
        }
        return newState;
    };
}
