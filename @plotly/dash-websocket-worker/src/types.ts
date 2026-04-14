/**
 * Message types for communication between renderer and worker.
 */
export enum WorkerMessageType {
    // Renderer -> Worker
    CONNECT = 'connect',
    DISCONNECT = 'disconnect',
    CALLBACK_REQUEST = 'callback_request',
    GET_PROPS_RESPONSE = 'get_props_response',

    // Worker -> Renderer
    CONNECTED = 'connected',
    DISCONNECTED = 'disconnected',
    CALLBACK_RESPONSE = 'callback_response',
    SET_PROPS = 'set_props',
    GET_PROPS_REQUEST = 'get_props_request',
    ERROR = 'error'
}

/**
 * Base message structure for worker communication.
 */
export interface WorkerMessage {
    type: WorkerMessageType;
    rendererId: string;
    requestId?: string;
    payload?: unknown;
}

/**
 * Message from renderer to worker requesting connection.
 */
export interface ConnectMessage extends WorkerMessage {
    type: WorkerMessageType.CONNECT;
    payload: {
        serverUrl: string;
    };
}

/**
 * Message from renderer to worker requesting disconnect.
 */
export interface DisconnectMessage extends WorkerMessage {
    type: WorkerMessageType.DISCONNECT;
}

/**
 * Callback request payload structure.
 */
export interface CallbackPayload {
    output: string;
    outputs: unknown[];
    inputs: unknown[];
    state?: unknown[];
    changedPropIds: string[];
    parsedChangedPropsIds?: string[];
}

/**
 * Message from renderer to worker with callback request.
 */
export interface CallbackRequestMessage extends WorkerMessage {
    type: WorkerMessageType.CALLBACK_REQUEST;
    payload: CallbackPayload;
}

/**
 * Message from worker to renderer with callback response.
 */
export interface CallbackResponseMessage extends WorkerMessage {
    type: WorkerMessageType.CALLBACK_RESPONSE;
    payload: {
        status: 'ok' | 'prevent_update' | 'error';
        data?: Record<string, unknown>;
        message?: string;
    };
}

/**
 * Message from worker to renderer to set component props.
 */
export interface SetPropsMessage extends WorkerMessage {
    type: WorkerMessageType.SET_PROPS;
    payload: {
        componentId: string;
        props: Record<string, unknown>;
    };
}

/**
 * Message from worker to renderer requesting prop values.
 */
export interface GetPropsRequestMessage extends WorkerMessage {
    type: WorkerMessageType.GET_PROPS_REQUEST;
    payload: {
        componentId: string;
        properties: string[];
    };
}

/**
 * Message from renderer to worker with prop values.
 */
export interface GetPropsResponseMessage extends WorkerMessage {
    type: WorkerMessageType.GET_PROPS_RESPONSE;
    payload: Record<string, unknown>;
}

/**
 * Error message from worker to renderer.
 */
export interface ErrorMessage extends WorkerMessage {
    type: WorkerMessageType.ERROR;
    payload: {
        message: string;
        code?: string;
    };
}

/**
 * Connected confirmation message from worker to renderer.
 */
export interface ConnectedMessage extends WorkerMessage {
    type: WorkerMessageType.CONNECTED;
}

/**
 * Disconnected notification message from worker to renderer.
 */
export interface DisconnectedMessage extends WorkerMessage {
    type: WorkerMessageType.DISCONNECTED;
    payload?: {
        reason?: string;
    };
}

/**
 * Union type of all possible worker messages.
 */
export type AnyWorkerMessage =
    | ConnectMessage
    | DisconnectMessage
    | CallbackRequestMessage
    | CallbackResponseMessage
    | SetPropsMessage
    | GetPropsRequestMessage
    | GetPropsResponseMessage
    | ErrorMessage
    | ConnectedMessage
    | DisconnectedMessage;
