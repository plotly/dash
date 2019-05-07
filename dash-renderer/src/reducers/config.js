/* global document:true */
import {getAction} from '../actions/constants';

export default function config(state = null, action) {
    if (action.type === getAction('READ_CONFIG')) {
        return JSON.parse(document.getElementById('_dash-config').textContent);
    }
    return state;
}
