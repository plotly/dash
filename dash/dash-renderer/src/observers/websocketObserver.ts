/**
 * Observer for handling incoming WebSocket messages (SET_PROPS, GET_PROPS_REQUEST).
 */

/* eslint-disable no-console */

import {Store} from 'redux';
import {path} from 'ramda';

import {IStoreState} from '../store';
import {updateProps, notifyObservers} from '../actions';
import {getPath} from '../actions/paths';
import {
    getWorkerClient,
    SetPropsPayload,
    GetPropsRequestPayload
} from '../utils/workerClient';
import {DashConfig} from '../config';

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
    // Initialize WebSocket if:
    // 1. Global websocket is enabled, OR
    // 2. WebSocket config is available (for per-callback websocket=True)
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

    // Handle SET_PROPS messages
    workerClient.onSetProps = (payload: SetPropsPayload) => {
        const {componentId, props} = payload;
        const state = store.getState();
        const componentPath = getPath(state.paths, componentId);

        if (!componentPath) {
            console.warn(
                `SET_PROPS: Component ${componentId} not found in layout`
            );
            return;
        }

        // Update the component props
        store.dispatch(
            updateProps({
                props,
                itempath: componentPath,
                renderType: 'websocket'
            }) as any
        );

        // Notify observers
        store.dispatch(notifyObservers({id: componentId, props}) as any);
    };

    // Handle GET_PROPS_REQUEST messages
    workerClient.onGetPropsRequest = (
        requestId: string,
        payload: GetPropsRequestPayload
    ) => {
        const {componentId, properties} = payload;
        const state = store.getState();
        const componentPath = getPath(state.paths, componentId);

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
        }

        // Send the response
        workerClient.sendGetPropsResponse(requestId, result);
    };

    // Handle connection events
    workerClient.onConnected = () => {
        console.log('[Dash] WebSocket connected');
    };

    workerClient.onDisconnected = (reason?: string) => {
        console.log(`[Dash] WebSocket disconnected: ${reason}`);
    };

    workerClient.onError = (message: string, code?: string) => {
        console.error(`[Dash] WebSocket error: ${message}`, code);
    };

    // Connect to the worker
    const wsUrl = buildWebSocketUrl(config);

    try {
        // config.websocket is guaranteed to exist due to wsAvailable check above
        await workerClient.connect(config.websocket!.worker_url, wsUrl);
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
