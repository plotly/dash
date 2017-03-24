import {ACTIONS} from '../actions/index.js';

export function APP_STATES(state) {
    const stateList = {
        'STARTED': 'STARTED',
        'INITIALIZED': 'INITIALIZED'
    }
    if (stateList[state]) return stateList[state];
    else throw new Error (`${state} is not a valid app state.`);
}

function appLifecycle(state=APP_STATES('STARTED'), action) {
    switch (action.type) {
        case ACTIONS('SET_APP_LIFECYCLE'):
            return APP_STATES(action.payload);
        default:
            return state;
    }
}

export default appLifecycle;
