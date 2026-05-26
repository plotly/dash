/**
 * Dash WebSocket Worker
 *
 * A SharedWorker that maintains a single WebSocket connection to the Dash server
 * and routes messages between multiple renderer instances (browser tabs).
 */

import { WebSocketManager } from './WebSocketManager';
import { MessageRouter } from './MessageRouter';
import {
    WorkerMessageType,
    WorkerMessage,
    ConnectMessage
} from './types';

// SharedWorker global scope
declare const self: SharedWorkerGlobalScope;

/** WebSocket connection manager */
const wsManager = new WebSocketManager();

/** Message router for renderers */
const router = new MessageRouter();

/** Current server URL */
let serverUrl: string | null = null;

/**
 * Set up WebSocket manager callbacks.
 */
wsManager.onOpen = () => {
    console.log('[DashWSWorker] WebSocket connected');
    // Notify all renderers that connection is established
    for (const rendererId of getRendererIds()) {
        router.notifyConnected(rendererId);
    }
};

wsManager.onClose = (reason?: string) => {
    console.log(`[DashWSWorker] WebSocket closed: ${reason}`);
    router.notifyDisconnected(reason);
};

wsManager.onMessage = (data: unknown) => {
    router.handleServerMessage(data);
};

wsManager.onError = (error: Error) => {
    console.error('[DashWSWorker] WebSocket error:', error.message);
};

/**
 * Set up router to send messages to WebSocket.
 */
router.sendToServer = (message: unknown) => {
    wsManager.send(message);
};

// Track renderer IDs separately for iteration
const rendererIds = new Set<string>();

/**
 * Get all registered renderer IDs.
 */
function getRendererIds(): string[] {
    return Array.from(rendererIds);
}

/**
 * Handle new connection from a renderer (browser tab).
 */
self.onconnect = (event: MessageEvent) => {
    const port = event.ports[0];

    port.onmessage = (e: MessageEvent) => {
        const message = e.data as WorkerMessage;

        switch (message.type) {
            case WorkerMessageType.CONNECT: {
                const connectMsg = message as ConnectMessage;
                const rendererId = connectMsg.rendererId;
                const newServerUrl = connectMsg.payload.serverUrl;
                const inactivityTimeout = connectMsg.payload.inactivityTimeout;

                // Register the renderer
                router.registerRenderer(rendererId, port);
                rendererIds.add(rendererId);

                console.log(`[DashWSWorker] Renderer ${rendererId} connected, inactivityTimeout: ${inactivityTimeout}`);

                // Update inactivity timeout if provided
                if (typeof inactivityTimeout === 'number') {
                    wsManager.setConfig({ inactivityTimeout });
                }

                // Connect to server if not already connected
                if (!wsManager.isConnected) {
                    if (serverUrl !== newServerUrl) {
                        serverUrl = newServerUrl;
                    }
                    wsManager.connect(serverUrl);
                } else {
                    // Already connected, notify the renderer
                    router.notifyConnected(rendererId);
                }
                break;
            }

            case WorkerMessageType.DISCONNECT: {
                const rendererId = message.rendererId;
                router.unregisterRenderer(rendererId);
                rendererIds.delete(rendererId);

                console.log(`[DashWSWorker] Renderer ${rendererId} disconnected`);

                // If no more renderers, disconnect from server
                if (router.rendererCount === 0) {
                    wsManager.disconnect();
                    serverUrl = null;
                    console.log('[DashWSWorker] All renderers disconnected, closing WebSocket');
                }
                break;
            }

            case WorkerMessageType.TAB_VISIBLE: {
                // Reset activity timer when tab becomes visible
                // This prevents inactivity timeout while user is viewing the tab
                wsManager.resetActivity();
                break;
            }

            default:
                // Forward other messages through the router
                router.handleRendererMessage(message.rendererId, message);
        }
    };

    port.start();
};

// Log worker startup
console.log('[DashWSWorker] SharedWorker initialized');
