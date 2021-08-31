import {getAction} from '../actions/constants';
import {mergeDeepRight} from 'ramda';

export default function config(state = null, action) {
    if (action.type === getAction('SET_CONFIG')) {
        return action.payload;
    } else if (action.type === getAction('ADD_HTTP_HEADERS')) {
        return mergeDeepRight(state, {
            fetch: {
                headers: action.payload
            }
        });
    }
    return state;
}
