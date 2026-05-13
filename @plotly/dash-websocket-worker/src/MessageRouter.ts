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
     * Messages may be batched as arrays for efficiency.
     * @param message The message from the server (single message or array)
     */
    public handleServerMessage(message: unknown): void {
        // Handle batched messages (array of messages)
        if (Array.isArray(message)) {
            this.handleBatchedMessages(message);
            return;
        }

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
     * Handle a batch of messages from the server.
     * Groups set_props by renderer and forwards as a single batch message.
     * @param messages Array of messages
     */
    private handleBatchedMessages(messages: unknown[]): void {
        // Group set_props by renderer, keep others separate
        const setPropsPayloadsByRenderer: Map<string, SetPropsMessage['payload'][]> = new Map();
        const otherMessages: WorkerMessage[] = [];

        for (const message of messages) {
            const msg = message as WorkerMessage;
            // Skip heartbeat_ack - already handled by WebSocketManager
            if ((msg as any).type === 'heartbeat_ack') {
                continue;
            }
            if (msg.type === WorkerMessageType.SET_PROPS) {
                const setPropsMsg = msg as SetPropsMessage;
                const rendererId = setPropsMsg.rendererId;
                if (!setPropsPayloadsByRenderer.has(rendererId)) {
                    setPropsPayloadsByRenderer.set(rendererId, []);
                }
                setPropsPayloadsByRenderer.get(rendererId)!.push(setPropsMsg.payload);
            } else {
                otherMessages.push(msg);
            }
        }

        // Forward batched set_props to each renderer
        for (const [rendererId, payloads] of setPropsPayloadsByRenderer) {
            const port = this.renderers.get(rendererId);
            if (port) {
                try {
                    port.postMessage({
                        type: WorkerMessageType.SET_PROPS_BATCH,
                        rendererId,
                        payload: payloads
                    });
                } catch (error) {
                    console.warn(`Failed to forward batch to renderer ${rendererId}, removing`);
                    this.renderers.delete(rendererId);
                }
            }
        }

        // Forward other messages individually
        for (const msg of otherMessages) {
            this.handleServerMessage(msg);
        }
    }

    /**
     * Send a message to all connected renderers.
     * @param message The message to broadcast
     */
    public broadcastToRenderers(message: WorkerMessage): void {
        for (const [rendererId, port] of this.renderers) {
            try {
                port.postMessage(message);
            } catch (error) {
                // Port may be closed if tab was closed
                console.warn(`Failed to send to renderer ${rendererId}, removing`);
                this.renderers.delete(rendererId);
            }
        }
    }

    /**
     * Send a connected notification to a specific renderer.
     * @param rendererId The renderer to notify
     */
    public notifyConnected(rendererId: string): void {
        const port = this.renderers.get(rendererId);
        if (port) {
            try {
                port.postMessage({
                    type: WorkerMessageType.CONNECTED,
                    rendererId
                });
            } catch (error) {
                console.warn(`Failed to notify renderer ${rendererId}, removing`);
                this.renderers.delete(rendererId);
            }
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
            try {
                port.postMessage({
                    type: WorkerMessageType.ERROR,
                    rendererId,
                    payload: { message, code }
                });
            } catch (error) {
                console.warn(`Failed to send error to renderer ${rendererId}, removing`);
                this.renderers.delete(rendererId);
            }
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
            try {
                port.postMessage(message);
            } catch (error) {
                console.warn(`Failed to forward to renderer ${rendererId}, removing`);
                this.renderers.delete(rendererId);
            }
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
