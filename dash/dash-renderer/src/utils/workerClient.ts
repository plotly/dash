/**
 * Client for communicating with the Dash WebSocket SharedWorker.
 */

import {getRendererId} from './rendererId';

/** Message types for worker communication */
export enum WorkerMessageType {
    CONNECT = 'connect',
    DISCONNECT = 'disconnect',
    CALLBACK_REQUEST = 'callback_request',
    GET_PROPS_RESPONSE = 'get_props_response',
    CONNECTED = 'connected',
    DISCONNECTED = 'disconnected',
    CALLBACK_RESPONSE = 'callback_response',
    SET_PROPS = 'set_props',
    GET_PROPS_REQUEST = 'get_props_request',
    ERROR = 'error'
}

/** Callback response structure */
export interface CallbackResponse {
    status: 'ok' | 'prevent_update' | 'error';
    data?: Record<string, unknown>;
    message?: string;
}

/** Set props message payload */
export interface SetPropsPayload {
    componentId: string;
    props: Record<string, unknown>;
}

/** Get props request payload */
export interface GetPropsRequestPayload {
    componentId: string;
    properties: string[];
}

/** Pending callback request */
interface PendingRequest {
    resolve: (value: CallbackResponse) => void;
    reject: (error: Error) => void;
}

/**
 * Client for the Dash WebSocket SharedWorker.
 */
class WorkerClient {
    private worker: SharedWorker | null = null;
    private rendererId: string;
    private pendingCallbacks: Map<string, PendingRequest> = new Map();
    private requestCounter = 0;
    private isConnected = false;
    private connectionPromise: Promise<void> | null = null;
    private connectionResolve: (() => void) | null = null;

    /** Callback when SET_PROPS message is received */
    public onSetProps: ((payload: SetPropsPayload) => void) | null = null;

    /** Callback when GET_PROPS_REQUEST message is received */
    public onGetPropsRequest:
        | ((requestId: string, payload: GetPropsRequestPayload) => void)
        | null = null;

    /** Callback when connection is established */
    public onConnected: (() => void) | null = null;

    /** Callback when connection is lost */
    public onDisconnected: ((reason?: string) => void) | null = null;

    /** Callback when an error occurs */
    public onError: ((message: string, code?: string) => void) | null = null;

    constructor() {
        this.rendererId = getRendererId();
    }

    /**
     * Initialize the worker connection.
     * @param workerUrl URL to the SharedWorker script
     * @param serverUrl WebSocket server URL
     * @param inactivityTimeout Optional inactivity timeout in ms
     */
    public async connect(
        workerUrl: string,
        serverUrl: string,
        inactivityTimeout?: number
    ): Promise<void> {
        if (this.worker) {
            // Already connected
            return;
        }

        // Create the SharedWorker
        this.worker = new SharedWorker(workerUrl, {
            name: 'dash-ws-worker'
        });

        // Set up message handling
        this.worker.port.onmessage = this.handleMessage.bind(this);

        // Create promise for connection
        this.connectionPromise = new Promise(resolve => {
            this.connectionResolve = resolve;
        });

        // Start the port
        this.worker.port.start();

        // Send connect message
        this.worker.port.postMessage({
            type: WorkerMessageType.CONNECT,
            rendererId: this.rendererId,
            payload: {
                serverUrl,
                inactivityTimeout
            }
        });

        // Wait for connection
        await this.connectionPromise;
    }

    /**
     * Disconnect from the worker.
     */
    public disconnect(): void {
        if (this.worker) {
            this.worker.port.postMessage({
                type: WorkerMessageType.DISCONNECT,
                rendererId: this.rendererId
            });
            this.worker.port.close();
            this.worker = null;
        }
        this.isConnected = false;
        this.connectionPromise = null;
        this.connectionResolve = null;

        // Reject any pending callbacks
        for (const [, pending] of this.pendingCallbacks) {
            pending.reject(new Error('Worker disconnected'));
        }
        this.pendingCallbacks.clear();
    }

    /**
     * Ensure the worker is connected, initiating connection if needed.
     * @param config The Dash config with websocket settings
     */
    public async ensureConnected(config: {
        websocket?: {
            url?: string;
            worker_url?: string;
            inactivity_timeout?: number;
        };
    }): Promise<void> {
        // Already connected
        if (this.isConnected) {
            return;
        }

        // Connection in progress, wait for it
        if (this.connectionPromise) {
            await this.connectionPromise;
            return;
        }

        // Need to initiate connection
        if (!config.websocket?.url || !config.websocket?.worker_url) {
            throw new Error('WebSocket config not available');
        }

        if (typeof SharedWorker === 'undefined') {
            throw new Error('SharedWorker not supported');
        }

        // Build WebSocket URL
        const wsProtocol =
            window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const wsUrl = `${wsProtocol}//${host}${config.websocket.url}`;

        await this.connect(
            config.websocket.worker_url,
            wsUrl,
            config.websocket.inactivity_timeout
        );
    }

    /**
     * Send a callback request to the server via the worker.
     * @param payload The callback payload
     * @returns Promise that resolves with the callback response
     */
    public async sendCallback(payload: unknown): Promise<CallbackResponse> {
        // Wait for initial connection if one is in progress
        if (this.connectionPromise && !this.isConnected) {
            await this.connectionPromise;
        }

        if (!this.worker) {
            throw new Error('Worker not connected');
        }

        const requestId = `${this.rendererId}-${++this.requestCounter}`;

        return new Promise((resolve, reject) => {
            this.pendingCallbacks.set(requestId, {resolve, reject});

            this.worker!.port.postMessage({
                type: WorkerMessageType.CALLBACK_REQUEST,
                rendererId: this.rendererId,
                requestId,
                payload
            });
        });
    }

    /**
     * Send a get_props response back to the server.
     * @param requestId The request ID from the get_props request
     * @param props The property values
     */
    public sendGetPropsResponse(
        requestId: string,
        props: Record<string, unknown>
    ): void {
        if (!this.worker || !this.isConnected) {
            return;
        }

        this.worker.port.postMessage({
            type: WorkerMessageType.GET_PROPS_RESPONSE,
            rendererId: this.rendererId,
            requestId,
            payload: props
        });
    }

    /**
     * Check if the worker is connected.
     */
    public get connected(): boolean {
        return this.isConnected;
    }

    private handleMessage(event: MessageEvent): void {
        const message = event.data;

        switch (message.type) {
            case WorkerMessageType.CONNECTED:
                this.isConnected = true;
                if (this.connectionResolve) {
                    this.connectionResolve();
                    this.connectionResolve = null;
                }
                if (this.onConnected) {
                    this.onConnected();
                }
                break;

            case WorkerMessageType.DISCONNECTED:
                this.isConnected = false;
                // Reject all pending callbacks so loading states don't stay on forever
                for (const [, pending] of this.pendingCallbacks) {
                    pending.reject(new Error('WebSocket disconnected'));
                }
                this.pendingCallbacks.clear();
                if (this.onDisconnected) {
                    this.onDisconnected(message.payload?.reason);
                }
                break;

            case WorkerMessageType.CALLBACK_RESPONSE: {
                const requestId = message.requestId;
                const pending = this.pendingCallbacks.get(requestId);
                if (pending) {
                    this.pendingCallbacks.delete(requestId);
                    pending.resolve(message.payload);
                }
                break;
            }

            case WorkerMessageType.SET_PROPS:
                if (this.onSetProps) {
                    this.onSetProps(message.payload);
                }
                break;

            case WorkerMessageType.GET_PROPS_REQUEST:
                if (this.onGetPropsRequest) {
                    this.onGetPropsRequest(message.requestId, message.payload);
                }
                break;

            case WorkerMessageType.ERROR:
                if (this.onError) {
                    this.onError(
                        message.payload?.message || 'Unknown error',
                        message.payload?.code
                    );
                }
                break;
        }
    }
}

// Singleton instance
let workerClientInstance: WorkerClient | null = null;

/**
 * Get the singleton WorkerClient instance.
 */
export function getWorkerClient(): WorkerClient {
    if (!workerClientInstance) {
        workerClientInstance = new WorkerClient();
    }
    return workerClientInstance;
}

/**
 * Check if WebSocket callbacks are globally enabled and supported.
 * @param config The Dash config
 */
export function isWebSocketEnabled(config: {
    websocket?: {enabled: boolean};
}): boolean {
    return !!(config.websocket?.enabled && typeof SharedWorker !== 'undefined');
}

/**
 * Check if WebSocket infrastructure is available (for per-callback websocket).
 * @param config The Dash config
 */
export function isWebSocketAvailable(config: {
    websocket?: {
        enabled?: boolean;
        url?: string;
        worker_url?: string;
        inactivity_timeout?: number;
    };
}): boolean {
    return !!(
        config.websocket?.url &&
        config.websocket?.worker_url &&
        typeof SharedWorker !== 'undefined'
    );
}
