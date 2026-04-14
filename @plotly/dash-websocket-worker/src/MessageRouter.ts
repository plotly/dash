import {
    WorkerMessageType,
    WorkerMessage,
    CallbackRequestMessage,
    GetPropsResponseMessage,
    SetPropsMessage,
    GetPropsRequestMessage,
    CallbackResponseMessage
} from './types';

/**
 * Routes messages between renderers (via MessagePorts) and the WebSocket server.
 */
export class MessageRouter {
    /** Map of renderer IDs to their MessagePorts */
    private renderers: Map<string, MessagePort> = new Map();

    /** Callback to send messages to the WebSocket server */
    public sendToServer: ((message: unknown) => void) | null = null;

    /**
     * Register a renderer with its MessagePort.
     * @param rendererId Unique identifier for the renderer
     * @param port The MessagePort for communication
     */
    public registerRenderer(rendererId: string, port: MessagePort): void {
        this.renderers.set(rendererId, port);
    }

    /**
     * Unregister a renderer.
     * @param rendererId The renderer to unregister
     */
    public unregisterRenderer(rendererId: string): void {
        this.renderers.delete(rendererId);
    }

    /**
     * Get the number of connected renderers.
     */
    public get rendererCount(): number {
        return this.renderers.size;
    }

    /**
     * Handle a message from a renderer.
     * @param rendererId The ID of the renderer that sent the message
     * @param message The message from the renderer
     */
    public handleRendererMessage(rendererId: string, message: WorkerMessage): void {
        switch (message.type) {
            case WorkerMessageType.CALLBACK_REQUEST:
                this.forwardCallbackRequest(rendererId, message as CallbackRequestMessage);
                break;

            case WorkerMessageType.GET_PROPS_RESPONSE:
                this.forwardGetPropsResponse(rendererId, message as GetPropsResponseMessage);
                break;

            default:
                console.warn(`Unknown message type from renderer: ${message.type}`);
        }
    }

    /**
     * Handle a message from the WebSocket server.
     * @param message The message from the server
     */
    public handleServerMessage(message: unknown): void {
        const msg = message as WorkerMessage;
        const rendererId = msg.rendererId;

        switch (msg.type) {
            case WorkerMessageType.CALLBACK_RESPONSE:
                this.forwardToRenderer(rendererId, msg as CallbackResponseMessage);
                break;

            case WorkerMessageType.SET_PROPS:
                this.forwardSetProps(rendererId, msg as SetPropsMessage);
                break;

            case WorkerMessageType.GET_PROPS_REQUEST:
                this.forwardGetPropsRequest(rendererId, msg as GetPropsRequestMessage);
                break;

            case WorkerMessageType.ERROR:
                this.forwardToRenderer(rendererId, msg);
                break;

            default:
                console.warn(`Unknown message type from server: ${msg.type}`);
        }
    }

    /**
     * Send a message to all connected renderers.
     * @param message The message to broadcast
     */
    public broadcastToRenderers(message: WorkerMessage): void {
        for (const [, port] of this.renderers) {
            port.postMessage(message);
        }
    }

    /**
     * Send a connected notification to a specific renderer.
     * @param rendererId The renderer to notify
     */
    public notifyConnected(rendererId: string): void {
        const port = this.renderers.get(rendererId);
        if (port) {
            port.postMessage({
                type: WorkerMessageType.CONNECTED,
                rendererId
            });
        }
    }

    /**
     * Send a disconnected notification to all renderers.
     * @param reason Optional reason for disconnection
     */
    public notifyDisconnected(reason?: string): void {
        this.broadcastToRenderers({
            type: WorkerMessageType.DISCONNECTED,
            rendererId: '',
            payload: { reason }
        });
    }

    /**
     * Send an error notification to a specific renderer.
     * @param rendererId The renderer to notify
     * @param message Error message
     * @param code Optional error code
     */
    public notifyError(rendererId: string, message: string, code?: string): void {
        const port = this.renderers.get(rendererId);
        if (port) {
            port.postMessage({
                type: WorkerMessageType.ERROR,
                rendererId,
                payload: { message, code }
            });
        }
    }

    private forwardCallbackRequest(rendererId: string, message: CallbackRequestMessage): void {
        if (this.sendToServer) {
            this.sendToServer({
                type: WorkerMessageType.CALLBACK_REQUEST,
                rendererId,
                requestId: message.requestId,
                payload: message.payload
            });
        }
    }

    private forwardGetPropsResponse(rendererId: string, message: GetPropsResponseMessage): void {
        if (this.sendToServer) {
            this.sendToServer({
                type: WorkerMessageType.GET_PROPS_RESPONSE,
                rendererId,
                requestId: message.requestId,
                payload: message.payload
            });
        }
    }

    private forwardToRenderer(rendererId: string, message: WorkerMessage): void {
        const port = this.renderers.get(rendererId);
        if (port) {
            port.postMessage(message);
        } else {
            console.warn(`Renderer ${rendererId} not found for message`);
        }
    }

    private forwardSetProps(rendererId: string, message: SetPropsMessage): void {
        this.forwardToRenderer(rendererId, message);
    }

    private forwardGetPropsRequest(rendererId: string, message: GetPropsRequestMessage): void {
        this.forwardToRenderer(rendererId, message);
    }
}
