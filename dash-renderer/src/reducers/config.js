import {getAction} from '../actions/constants';

export default function config(state = null, action) {
    if (action.type === getAction('SET_CONFIG')) {
        return action.payload;
    }
    return state;
}
