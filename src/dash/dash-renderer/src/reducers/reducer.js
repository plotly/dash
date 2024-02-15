import {forEach, isEmpty, keys, path} from 'ramda';
import {combineReducers} from 'redux';

import {getCallbacksByInput} from '../actions/dependencies_ts';

import createApiReducer from './api';
import appLifecycle from './appLifecycle';
import callbacks from './callbacks';
import config from './config';
import graphs from './dependencyGraph';
import error from './error';
import history from './history';
import hooks from './hooks';
import profile from './profile';
import changed from './changed';
import isLoading from './isLoading';
import layout from './layout';
import loadingMap from './loadingMap';
import paths from './paths';
import callbackJobs from './callbackJobs';

export const apiRequests = [
    'dependenciesRequest',
    'layoutRequest',
    'reloadRequest',
    'loginRequest'
];

function mainReducer() {
    const parts = {
        appLifecycle,
        callbacks,
        config,
        error,
        graphs,
        history,
        hooks,
        profile,
        changed,
        isLoading,
        layout,
        loadingMap,
        paths
    };
    forEach(r => {
        parts[r] = createApiReducer(r);
    }, apiRequests);

    parts.callbackJobs = callbackJobs;

    return combineReducers(parts);
}

function getInputHistoryState(payload, state, recordChanges) {
    const {graphs, paths, layout} = state;
    const {itempath, props} = payload;
    const refProps = path(itempath.concat(['props']), layout) || {};
    const {id} = refProps;

    let historyEntry;
    if (id) {
        if (recordChanges) {
            state.changed = {id, props};
        }

        historyEntry = {id, props: {}};
        keys(props).forEach(propKey => {
            if (getCallbacksByInput(graphs, paths, id, propKey).length) {
                historyEntry.props[propKey] = refProps[propKey];
            }
        });
    }
    return historyEntry;
}

function recordHistory(reducer) {
    return function (state, action) {
        // Record initial state
        const {type, payload} = action;
        if (type === 'ON_PROP_CHANGE') {
            // history records all prop changes that are inputs.
            const historyEntry = getInputHistoryState(payload, state, true);
            if (historyEntry && !isEmpty(historyEntry.props)) {
                state.history.present = historyEntry;
            }
        }

        const nextState = reducer(state, action);

        if (type === 'ON_PROP_CHANGE' && payload.source !== 'response') {
            /*
             * if the prop change is an input, then
             * record it so that it can be played back
             */
            const historyEntry = getInputHistoryState(payload, nextState);
            if (historyEntry && !isEmpty(historyEntry.props)) {
                nextState.history = {
                    past: [...nextState.history.past, state.history.present],
                    present: historyEntry,
                    future: []
                };
            }
        }

        return nextState;
    };
}

function reloaderReducer(reducer) {
    return function (state, action) {
        const {history, config, hooks} = state || {};
        let newState = state;
        if (action.type === 'RELOAD') {
            newState = {history, config, hooks};
        } else if (action.type === 'SET_CONFIG') {
            // new config also reloads, and even clears history,
            // in case there's a new user or even a totally different app!
            // hooks are set at an even higher level than config though.
            newState = {hooks};
        }
        return reducer(newState, action);
    };
}

export function createReducer() {
    return reloaderReducer(recordHistory(mainReducer()));
}
