import {getAction} from '../actions/constants';

export default function config(state = false, action) {
    if (action.type === getAction('SET_APP_READY')) {
        return action.payload;
    }
    return state;
}
