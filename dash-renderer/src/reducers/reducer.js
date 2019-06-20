'use strict';
import R, {concat, lensPath, view} from 'ramda';
import {combineReducers} from 'redux';
import layout from './layout';
import graphs from './dependencyGraph';
import paths from './paths';
import requestQueue from './requestQueue';
import appLifecycle from './appLifecycle';
import history from './history';
import error from './error';
import hooks from './hooks';
import * as API from './api';
import config from './config';

const reducer = combineReducers({
    appLifecycle,
    layout,
    graphs,
    paths,
    requestQueue,
    config,
    history,
    error,
    hooks,
    dependenciesRequest: API.dependenciesRequest,
    layoutRequest: API.layoutRequest,
    reloadRequest: API.reloadRequest,
    loginRequest: API.loginRequest,
});

function getInputHistoryState(itempath, props, state) {
    const {graphs, layout, paths} = state;
    const {InputGraph} = graphs;
    const keyObj = R.filter(R.equals(itempath), paths);
    let historyEntry;
    if (!R.isEmpty(keyObj)) {
        const id = R.keys(keyObj)[0];
        historyEntry = {id, props: {}};
        R.keys(props).forEach(propKey => {
            const inputKey = `${id}.${propKey}`;
            if (
                InputGraph.hasNode(inputKey) &&
                InputGraph.dependenciesOf(inputKey).length > 0
            ) {
                historyEntry.props[propKey] = view(
                    lensPath(concat(paths[id], ['props', propKey])),
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
            if (historyEntry && !R.isEmpty(historyEntry.props)) {
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
            if (historyEntry && !R.isEmpty(historyEntry.props)) {
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
        if (action.type === 'RELOAD') {
            const {history, config} = state;
            // eslint-disable-next-line no-param-reassign
            state = {history, config};
        }
        return reducer(state, action);
    };
}

export default reloaderReducer(recordHistory(reducer));
