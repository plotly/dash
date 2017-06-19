import {ACTIONS} from '../actions/constants';

export default function config (state = null, action) {
    if (action.type === ACTIONS('READ_CONFIG')) {
        return JSON.parse(document.getElementById('_dash-config').textContent);
    } else {
        return state;
    }
}
