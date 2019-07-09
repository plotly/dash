import {assoc, assocPath, mergeRight} from 'ramda';

export default function createApiReducer(store) {
    return function ApiReducer(state = {}, action) {
        let newState = state;
        if (action.type === store) {
            const {payload, status, content} = action;
            const newRequest = {status, content};
            if (Array.isArray(payload.id)) {
                newState = assocPath(payload.id, newRequest, state);
            } else if (payload.id) {
                newState = assoc(payload.id, newRequest, state);
            } else {
                newState = mergeRight(state, newRequest);
            }
        }
        return newState;
    };
}
