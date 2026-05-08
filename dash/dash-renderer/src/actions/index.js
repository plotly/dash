import {once, path} from 'ramda';
import {createAction} from 'redux-actions';
import {addRequestedCallbacks} from './callbacks';
import {getAppState} from '../reducers/constants';
import {getAction} from './constants';
import * as cookie from 'cookie';
import {validateCallbacksToLayout} from './dependencies';
import {
    includeObservers,
    getLayoutCallbacks,
    makeResolvedCallback,
    resolveDeps
} from './dependencies_ts';
import {computePaths, getPath} from './paths';
import {recordUiEdit} from '../persistence';

export const onError = createAction(getAction('ON_ERROR'));
export const setAppLifecycle = createAction(getAction('SET_APP_LIFECYCLE'));
export const setConfig = createAction(getAction('SET_CONFIG'));
export const addHttpHeaders = createAction(getAction('ADD_HTTP_HEADERS'));
export const setGraphs = createAction(getAction('SET_GRAPHS'));
export const setHooks = createAction(getAction('SET_HOOKS'));
export const setLayout = createAction(getAction('SET_LAYOUT'));
export const setPaths = createAction(getAction('SET_PATHS'));
export const setRequestQueue = createAction(getAction('SET_REQUEST_QUEUE'));
export const insertComponent = createAction(getAction('INSERT_COMPONENT'));
export const removeComponent = createAction(getAction('REMOVE_COMPONENT'));

export const onPropChange = createAction(getAction('ON_PROP_CHANGE'));
export const resetComponentState = createAction(
    getAction('RESET_COMPONENT_STATE')
);

export function updateProps(payload) {
    return (dispatch, getState) => {
        const component = path(payload.itempath, getState().layout);
        recordUiEdit(component, payload.props, dispatch);
        dispatch(onPropChange(payload));
    };
}

export const addComponentToLayout = payload => (dispatch, getState) => {
    const {paths} = getState();
    dispatch(insertComponent(payload));
    dispatch(
        setPaths(computePaths(payload.component, payload.componentPath, paths))
    );
};

export const dispatchError = dispatch => (message, lines) =>
    dispatch(
        onError({
            type: 'backEnd',
            error: {message, html: lines.join('\n')}
        })
    );

export function hydrateInitialOutputs() {
    return function (dispatch, getState) {
        validateCallbacksToLayout(getState(), dispatchError(dispatch));
        triggerDefaultState(dispatch, getState);
        dispatch(setAppLifecycle(getAppState('HYDRATED')));
    };
}

/* eslint-disable-next-line no-console */
const logWarningOnce = once(console.warn);

export function getCSRFHeader(config) {
    try {
        const tokenName = (config && config.csrf_token_name) || '_csrf_token';
        const headerName = (config && config.csrf_header_name) || 'X-CSRFToken';
        const cookies = cookie.parse(document.cookie);
        const token = cookies[tokenName];
        if (!token) {
            return {};
        }
        return {[headerName]: token};
    } catch (e) {
        logWarningOnce(e);
        return {};
    }
}

function triggerDefaultState(dispatch, getState) {
    const {graphs, paths, layout} = getState();

    // overallOrder will assert circular dependencies for multi output.
    try {
        graphs.MultiGraph.overallOrder();
    } catch (err) {
        dispatch(
            onError({
                type: 'backEnd',
                error: {
                    message: 'Circular Dependencies',
                    html: err.toString()
                }
            })
        );
    }

    const layoutCallbacks = getLayoutCallbacks(
        graphs,
        paths,
        layout.components,
        {
            outputsOnly: true
        }
    );

    // Also include no-output callbacks whose inputs are in the layout (or have no inputs)
    const noOutputCallbacks = (graphs.callbacks || [])
        .filter(cb => cb.noOutput && !cb.prevent_initial_call)
        .map(cb => {
            const resolved = makeResolvedCallback(cb, resolveDeps(), '');
            resolved.initialCall = true;
            return resolved;
        })
        .filter(cb => {
            // If no inputs, always include (fires once on initial load)
            if (cb.callback.inputs.length === 0) {
                return true;
            }
            // Check if any input is in the layout
            const inputs = cb.getInputs(paths);
            return inputs.some(inp =>
                Array.isArray(inp) ? inp.length > 0 : inp
            );
        });

    // Also include no-input callbacks (with outputs) that should fire on initial load
    const noInputCallbacks = (graphs.callbacks || [])
        .filter(
            cb =>
                !cb.noOutput &&
                cb.inputs.length === 0 &&
                !cb.prevent_initial_call
        )
        .map(cb => {
            const resolved = makeResolvedCallback(cb, resolveDeps(), '');
            resolved.initialCall = true;
            return resolved;
        })
        .filter(cb => {
            // Check if any output is in the layout
            const outputs = cb.getOutputs(paths);
            return outputs.some(out =>
                Array.isArray(out) ? out.length > 0 : out
            );
        });

    dispatch(
        addRequestedCallbacks([
            ...layoutCallbacks,
            ...noOutputCallbacks,
            ...noInputCallbacks
        ])
    );
}

export const redo = moveHistory('REDO');
export const undo = moveHistory('UNDO');
export const revert = moveHistory('REVERT');

function moveHistory(changeType) {
    return function (dispatch, getState) {
        const {history, paths} = getState();
        dispatch(createAction(changeType)());
        const {id, props} =
            (changeType === 'REDO'
                ? history.future[0]
                : history.past[history.past.length - 1]) || {};
        if (id) {
            // Update props
            dispatch(
                createAction('UNDO_PROP_CHANGE')({
                    itempath: getPath(paths, id),
                    props
                })
            );

            dispatch(notifyObservers({id, props}));
        }
    };
}

export function notifyObservers({id, props}) {
    return async function (dispatch, getState) {
        const {graphs, paths} = getState();
        dispatch(
            addRequestedCallbacks(includeObservers(id, props, graphs, paths))
        );
    };
}

export function handleAsyncError(err, message, dispatch) {
    // Handle html error responses
    if (err && typeof err.text === 'function') {
        err.text().then(text => {
            const error = {message, html: text};
            dispatch(onError({type: 'backEnd', error}));
        });
    } else {
        const error = err instanceof Error ? err : {message, html: err};
        dispatch(onError({type: 'backEnd', error}));
    }
}
