import {assoc, assocPath, mergeRight} from 'ramda';

export default function createApiReducer(store) {
    return function ApiReducer(state = {}, action) {
        let newState = state;
        if (action.type === store) {
            const {id, status, content} = action.payload;
            const newRequest = {status, content};
            if (Array.isArray(id)) {
                newState = assocPath(id, newRequest, state);
            } else if (id) {
                newState = assoc(id, newRequest, state);
            } else {
                newState = mergeRight(state, newRequest);
            }
        }
        return newState;
    };
}
