/**
 * Observer for handling incoming WebSocket messages (SET_PROPS, GET_PROPS_REQUEST).
 */

/* eslint-disable no-console */

import {Store} from 'redux';
import {path} from 'ramda';

import {IStoreState} from '../store';
import {updateProps, notifyObservers, setPaths} from '../actions';
import {parsePatchProps} from '../actions/patch';
import {computePaths, getPath} from '../actions/paths';
import {batch} from 'react-redux';
import {
    getWorkerClient,
    SetPropsPayload,
    GetPropsRequestPayload
} from '../utils/workerClient';
import {DashConfig} from '../config';
import {addRequestedCallbacks} from '../actions/callbacks';
import {makeResolvedCallback, resolveDeps} from '../actions/dependencies_ts';

/**
 * Parse a component ID that may be a stringified JSON object.
 * This handles dict IDs like '{"index":0,"type":"output"}' that need
 * to be parsed back to objects for getPath to work correctly.
 */
function parseComponentId(
    componentId: string
): string | Record<string, unknown> {
    if (componentId.startsWith('{') && componentId.endsWith('}')) {
        try {
            return JSON.parse(componentId);
        } catch {
            // Not valid JSON, return as-is
            return componentId;
        }
    }
    return componentId;
}

/**
 * Initialize the WebSocket observer.
 *
 * Sets up handlers for:
 * - SET_PROPS: Update component props when received from server
 * - GET_PROPS_REQUEST: Send current prop values back to server
 *
 * @param store Redux store
 * @param config Dash configuration
 */
export async function initializeWebSocket(
    store: Store<IStoreState>,
    config: DashConfig
): Promise<void> {
    // Register the observer whenever the backend exposes websocket
    // infrastructure. The handlers below are set up in both cases, but the
    // socket is only opened eagerly when websocket callbacks are enabled
    // globally (see the end of this function). When only per-callback
    // websocket=True is used, the connection is opened lazily on first dispatch
    // (handleWebsocketCallback -> workerClient.ensureConnected).
    const wsAvailable = !!(
        config.websocket?.url && config.websocket?.worker_url
    );
    if (!wsAvailable) {
        return;
    }

    // Check if SharedWorker is supported
    if (typeof SharedWorker === 'undefined') {
        console.warn(
            'SharedWorker not supported in this browser. ' +
                'WebSocket callbacks will fall back to HTTP.'
        );
        return;
    }

    const workerClient = getWorkerClient();

    // Helper to process a single set_props payload
    const processSetProps = (payload: SetPropsPayload) => {
        const {componentId, props: rawProps} = payload;
        const parsedId = parseComponentId(componentId);
        const state = store.getState();
        const componentPath = getPath(state.paths, parsedId);

        if (!componentPath) {
            console.warn(
                `SET_PROPS: Component ${componentId} not found in layout`
            );
            return;
        }

        // Get old component for Patch processing and path recomputation
        const oldComponent = path(componentPath, state.layout) as Record<
            string,
            unknown
        > | null;
        const oldProps = (oldComponent?.props || {}) as Record<string, unknown>;

        // Process props to handle Patch objects
        const processedProps = parsePatchProps(rawProps, oldProps);

        // Update the component props
        store.dispatch(
            updateProps({
                props: processedProps,
                itempath: componentPath,
                renderType: 'websocket'
            }) as any
        );

        // Notify observers
        store.dispatch(
            notifyObservers({id: parsedId, props: processedProps}) as any
        );

        // Recompute paths for any new child components
        if (oldComponent) {
            const updatedState = store.getState();
            store.dispatch(
                setPaths(
                    computePaths(
                        {
                            ...oldComponent,
                            props: {...oldProps, ...processedProps}
                        },
                        [...componentPath],
                        updatedState.paths,
                        updatedState.paths.events
                    )
                ) as any
            );
        }
    };

    // Handle single SET_PROPS message
    workerClient.onSetProps = processSetProps;

    // Handle batched SET_PROPS_BATCH message
    workerClient.onSetPropsBatch = (payloads: SetPropsPayload[]) => {
        batch(() => {
            for (const payload of payloads) {
                processSetProps(payload);
            }
        });
    };

    // Handle GET_PROPS_REQUEST messages
    workerClient.onGetPropsRequest = (
        requestId: string,
        payload: GetPropsRequestPayload
    ) => {
        const {componentId, properties} = payload;
        const parsedId = parseComponentId(componentId);
        const state = store.getState();
        const componentPath = getPath(state.paths, parsedId);

        const result: Record<string, unknown> = {};

        if (componentPath) {
            const componentProps = path(
                [...componentPath, 'props'],
                state.layout
            ) as Record<string, unknown> | undefined;

            if (componentProps) {
                for (const propName of properties) {
                    result[propName] = componentProps[propName];
                }
            }
        } else {
            console.warn(
                `GET_PROPS_REQUEST: Component ${componentId} not found in layout`
            );
        }

        // Send the response
        workerClient.sendGetPropsResponse(requestId, result);
    };

    // Track connection state for reconnection handling
    let wasDisconnected = false;

    // Handle connection events
    workerClient.onConnected = () => {
        console.log('[Dash] WebSocket connected');

        // On reconnect (not initial connect), re-trigger persistent callbacks
        if (wasDisconnected) {
            console.log(
                '[Dash] Reconnected - re-triggering persistent callbacks'
            );
            const state = store.getState();
            const {graphs} = state;

            if (graphs?.callbacks) {
                const persistentCallbacks = graphs.callbacks.reduce(
                    (acc: any[], cb: any) => {
                        // Only re-trigger no-output callbacks with no inputs
                        // These are the "persistent" callbacks that should restart
                        if (cb.noOutput && cb.inputs.length === 0) {
                            const resolved = makeResolvedCallback(
                                cb,
                                resolveDeps(),
                                ''
                            );
                            resolved.initialCall = true;
                            acc.push(resolved);
                        }
                        return acc;
                    },
                    []
                );

                if (persistentCallbacks.length > 0) {
                    console.log(
                        `[Dash] Re-triggering ${persistentCallbacks.length} persistent callback(s)`
                    );
                    store.dispatch(addRequestedCallbacks(persistentCallbacks));
                }
            }
        }
    };

    workerClient.onDisconnected = (reason?: string) => {
        console.log(`[Dash] WebSocket disconnected: ${reason}`);
        wasDisconnected = true;
    };

    workerClient.onError = (message: string, code?: string) => {
        console.error(`[Dash] WebSocket error: ${message}`, code);
    };

    // Handle tab visibility changes. Only reconnect a socket that was
    // previously established (wasDisconnected); never open the first connection
    // here, so apps without an active websocket callback stay socket-free.
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            if (workerClient.connected) {
                // Tab visible and connected - reset inactivity timer
                workerClient.notifyTabVisible();
            } else if (wasDisconnected) {
                // Tab visible but dropped - reconnect
                console.log('[Dash] Tab visible, reconnecting WebSocket...');
                workerClient
                    .ensureConnected(config)
                    .catch(err =>
                        console.error('[Dash] Failed to reconnect:', err)
                    );
            }
        }
    });

    // Only open the socket eagerly when websocket callbacks are enabled
    // globally. With only per-callback websocket=True, the handlers above stay
    // registered but no socket is opened until a websocket callback actually
    // runs and calls ensureConnected.
    if (!config.websocket?.enabled) {
        return;
    }

    // Connect to the worker
    const wsUrl = buildWebSocketUrl(config);

    try {
        // config.websocket is guaranteed to exist due to wsAvailable check above
        await workerClient.connect(
            config.websocket!.worker_url,
            wsUrl,
            config.websocket!.inactivity_timeout
        );
    } catch (error) {
        console.error('[Dash] Failed to connect to WebSocket worker:', error);
    }
}

/**
 * Build the WebSocket URL from config.
 */
function buildWebSocketUrl(config: DashConfig): string {
    if (!config.websocket?.url) {
        throw new Error('WebSocket URL not configured');
    }

    // Convert HTTP(S) URL to WS(S)
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;

    // The config.websocket.url is a path like "/_dash-ws-callback"
    return `${wsProtocol}//${host}${config.websocket.url}`;
}

/**
 * Disconnect from the WebSocket.
 */
export function disconnectWebSocket(): void {
    const workerClient = getWorkerClient();
    workerClient.disconnect();
}
