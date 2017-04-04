import {ACTIONS} from '../actions/constants';
import {APP_STATES} from './constants';

function appLifecycle(state=APP_STATES('STARTED'), action) {
    switch (action.type) {
        case ACTIONS('SET_APP_LIFECYCLE'):
            return APP_STATES(action.payload);
        default:
            return state;
    }
}

export default appLifecycle;
