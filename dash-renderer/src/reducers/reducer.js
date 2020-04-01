import {
    concat,
    equals,
    filter,
    forEach,
    isEmpty,
    keys,
    lensPath,
    view,
} from 'ramda';
import {combineReducers} from 'redux';
import layout from './layout';
import graphs from './dependencyGraph';
import paths from './paths';
import pendingCallbacks from './pendingCallbacks';
import appLifecycle from './appLifecycle';
import history from './history';
import error from './error';
import hooks from './hooks';
import createApiReducer from './api';
import config from './config';

export const apiRequests = [
    'dependenciesRequest',
    'layoutRequest',
    'reloadRequest',
    'loginRequest',
];

function mainReducer() {
    const parts = {
        appLifecycle,
        layout,
        graphs,
        paths,
        pendingCallbacks,
        config,
        history,
        error,
        hooks,
    };
    forEach(r => {
        parts[r] = createApiReducer(r);
    }, apiRequests);

    return combineReducers(parts);
}

function getInputHistoryState(itempath, props, state) {
    const {graphs, layout, paths} = state;
    const {InputGraph} = graphs;
    const keyObj = filter(equals(itempath), paths.strs);
    let historyEntry;
    if (!isEmpty(keyObj)) {
        const id = keys(keyObj)[0];
        historyEntry = {id, props: {}};
        keys(props).forEach(propKey => {
            const inputKey = `${id}.${propKey}`;
            if (
                InputGraph.hasNode(inputKey) &&
                InputGraph.dependenciesOf(inputKey).length > 0
            ) {
                historyEntry.props[propKey] = view(
                    lensPath(concat(paths.strs[id], ['props', propKey])),
                    layout
                );
            }
        });
    }
    return historyEntry;
}

function recordHistory(reducer) {
    return function(state, action) {
        // Record initial state
        if (action.type === 'ON_PROP_CHANGE') {
            const {itempath, props} = action.payload;
            const historyEntry = getInputHistoryState(itempath, props, state);
            if (historyEntry && !isEmpty(historyEntry.props)) {
                state.history.present = historyEntry;
            }
        }

        const nextState = reducer(state, action);

        if (
            action.type === 'ON_PROP_CHANGE' &&
            action.payload.source !== 'response'
        ) {
            const {itempath, props} = action.payload;
            /*
             * if the prop change is an input, then
             * record it so that it can be played back
             */
            const historyEntry = getInputHistoryState(
                itempath,
                props,
                nextState
            );
            if (historyEntry && !isEmpty(historyEntry.props)) {
                nextState.history = {
                    past: [...nextState.history.past, state.history.present],
                    present: historyEntry,
                    future: [],
                };
            }
        }

        return nextState;
    };
}

function reloaderReducer(reducer) {
    return function(state, action) {
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
