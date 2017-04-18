/* global window:true, document:true */
'use strict'
import R from 'ramda';
import {concat, lensPath, view} from 'ramda';
import {combineReducers} from 'redux';
import layout from './layout';
import graphs from './dependencyGraph';
import paths from './paths';
import requestQueue from './requestQueue';
import appLifecycle from './appLifecycle';
import history from './history';
import * as API from './api';
import {serialize} from '../actions/index';
import {APP_STATES} from './constants';

const reducer = combineReducers({
    appLifecycle,
    layout,
    graphs,
    paths,
    requestQueue,
    configRequest: API.configRequest,
    dependenciesRequest: API.dependenciesRequest,
    layoutRequest: API.layoutRequest,
    routesRequest: API.routesRequest,
    loginRequest: API.loginRequest,
    history
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
            if (InputGraph.dependenciesOf(inputKey).length > 0) {
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
    return function (state, action) {
        // Record initial state
        if (action.type === 'ON_PROP_CHANGE' &&
            R.isEmpty(state.history.present)
        ) {
            const {itempath, props} = action.payload;
            const historyEntry = getInputHistoryState(itempath, props, state);
            if (historyEntry && !R.isEmpty(historyEntry.props)) {
                state.history.present = historyEntry;
            }
        }

        const nextState = reducer(state, action);

        if (action.type === 'ON_PROP_CHANGE' &&
            action.payload.source !== 'response'
        ) {
            const {itempath, props} = action.payload;
            /*
             * if the prop change is an input, then
             * record it so that it can be played back
             */
            const historyEntry = getInputHistoryState(itempath, props, nextState);
            if (historyEntry && !R.isEmpty(historyEntry.props)) {

                nextState.history = {
                    past: [
                        ...nextState.history.past,
                        nextState.history.present
                    ],
                    present: historyEntry,
                    future: []
                }

            }
        }

        return nextState;

    }
}

function updateUrlPath(reducer) {
    return function(state, action) {
        const nextState = reducer(state, action);
        if (nextState.routesRequest.status === 200 &&
            nextState.appLifecycle == APP_STATES('HYDRATED')
        ) {
            const serialized = serialize(nextState);
            const matchingRoute = R.filter(route => R.equals(
                route.state,
                R.pick(R.keys(route.state), serialized)
            ), nextState.routesRequest.content);
            if (matchingRoute.length === 1 &&
                window.location.pathname !== matchingRoute[0].pathname
            ) {
                window.history.pushState(
                    {},
                    document.title,matchingRoute[0].pathname
                );
            } else if (matchingRoute.length > 1) {
                const nMostMatchedKeys = R.reduce(
                    (n, route) => R.max(n, R.keys(route.state).length),
                    0, matchingRoute
                );
                const bestMatchedRoute = matchingRoute.filter(route =>
                    R.keys(route.state).length === nMostMatchedKeys
                );
                if (bestMatchedRoute.length > 1) {
                    /* eslint-disable no-console */
                    console.error('Multiple URLs matched?', matchingRoute);
                    /* eslint-enable no-console */
                } else {
                    window.history.pushState(
                        {},
                        document.title,
                        bestMatchedRoute[0].pathname
                    );
                }
            }
        }
        return nextState;
    }
}

export default updateUrlPath(recordHistory(reducer));
