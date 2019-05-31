import {getAction} from '../actions/constants';
import {getAppState} from './constants';

function appLifecycle(state = getAppState('STARTED'), action) {
    switch (action.type) {
        case getAction('SET_APP_LIFECYCLE'):
            return getAppState(action.payload);
        default:
            return state;
    }
}

export default appLifecycle;
