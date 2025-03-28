import {forEach, includes, isEmpty, keys, path, assoc, pathOr} from 'ramda';
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
import paths from './paths';
import callbackJobs from './callbackJobs';
import loading from './loading';
import {stringifyPath} from '../wrapper/wrapping';

export const apiRequests = [
    'dependenciesRequest',
    'layoutRequest',
    'reloadRequest',
    'loginRequest'
];

function handleChildrenPropsUpdate({
    component,
    config,
    action,
    actionPath,
    state
}) {
    const childrenProps = pathOr(
        [],
        ['children_props', component?.namespace, component?.type],
        config
    );

    // Ensure "children" is always considered
    if (!childrenProps.includes('children')) {
        childrenProps.push('children');
    }

    childrenProps.forEach(childrenProp => {
        const segments = childrenProp.split('.');
        const includesArray = childrenProp.includes('[]');
        const includesObject = childrenProp.includes('{}');

        const cleanSegments = segments.map(s =>
            s.replace('[]', '').replace('{}', '')
        );

        const getFrontBack = () => {
            const front = [];
            const back = [];
            let found = false;

            for (const segment of segments) {
                const clean = segment.replace('{}', '').replace('[]', '');
                if (
                    !found &&
                    (segment.includes('[]') || segment.includes('{}'))
                ) {
                    found = true;
                    front.push(clean);
                } else if (found) {
                    back.push(clean);
                } else {
                    front.push(clean);
                }
            }

            return [front, back];
        };

        const [frontPath, backPath] = getFrontBack();
        const basePath = [...actionPath, 'props', ...frontPath];
        const propRoot = pathOr({}, ['payload', 'props'], action);

        if (!(cleanSegments[0] in propRoot)) return;

        const _fullValue = path(cleanSegments, propRoot);
        const fullValues = Array.isArray(_fullValue)
            ? _fullValue
            : [_fullValue];

        fullValues.forEach((fullValue, y) => {
            if (includesArray) {
                if (Array.isArray(fullValue)) {
                    fullValue.forEach((el, i) => {
                        let value = el;
                        if (includesObject && backPath.length) {
                            value = path(backPath, el);
                        }

                        if (value) {
                            const itempath = [...basePath, i, ...backPath];
                            state = adjustHashes(state, {
                                payload: {
                                    itempath,
                                    props: value?.props,
                                    component: value,
                                    config
                                }
                            });
                        }
                    });
                } else if (
                    fullValue &&
                    typeof fullValue === 'object' &&
                    !('props' in fullValue)
                ) {
                    Object.entries(fullValue).forEach(([key, value]) => {
                        const finalVal = backPath.length
                            ? path(backPath, value)
                            : value;
                        if (finalVal) {
                            const itempath = [...basePath, y, key, ...backPath];
                            state = adjustHashes(state, {
                                payload: {
                                    itempath,
                                    props: finalVal?.props,
                                    component: finalVal,
                                    config
                                }
                            });
                        }
                    });
                } else if (fullValue) {
                    const itempath = [...basePath, ...backPath];
                    if (Array.isArray(_fullValue)) {
                        itempath.push(y);
                    }
                    state = adjustHashes(state, {
                        payload: {
                            itempath,
                            props: fullValue?.props,
                            component: fullValue,
                            config
                        }
                    });
                }
            } else if (includesObject) {
                if (fullValue && typeof fullValue === 'object') {
                    Object.entries(fullValue).forEach(([key, value]) => {
                        const finalVal = backPath.length
                            ? path(backPath, value)
                            : value;
                        if (finalVal) {
                            const itempath = [...basePath, key, ...backPath];
                            state = adjustHashes(state, {
                                payload: {
                                    itempath,
                                    props: finalVal?.props,
                                    component: finalVal,
                                    config
                                }
                            });
                        }
                    });
                }
            } else {
                if (fullValue) {
                    const itempath = [...actionPath, 'props', ...cleanSegments];
                    if (Array.isArray(_fullValue)) {
                        itempath.push(y);
                    }
                    state = adjustHashes(state, {
                        payload: {
                            itempath,
                            props: fullValue?.props,
                            component: fullValue,
                            config
                        }
                    });
                }
            }
        });
    });

    return state;
}

function adjustHashes(state, action) {
    const actionPath = action.payload.itempath;
    const strPath = stringifyPath(actionPath);
    const prev = pathOr(0, [strPath], state);
    const {component, config} = action.payload;
    state = assoc(strPath, prev + 1, state);
    state = handleChildrenPropsUpdate({
        component,
        config,
        action,
        actionPath,
        state
    });
    return state;
}

const layoutHashes = (state = {}, action) => {
    if (
        includes(action.type, [
            'UNDO_PROP_CHANGE',
            'REDO_PROP_CHANGE',
            'ON_PROP_CHANGE'
        ])
    ) {
        // Let us compare the paths sums to get updates without triggering
        // render on the parent containers.
        return adjustHashes(state, action);
    }
    return state;
};

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
        paths,
        layoutHashes,
        loading
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
