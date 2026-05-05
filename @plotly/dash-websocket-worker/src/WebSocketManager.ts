/**
 * Configuration options for WebSocket connection.
 */
interface WebSocketConfig {
    /** Maximum number of reconnection attempts */
    maxRetries: number;
    /** Initial delay between reconnection attempts (ms) */
    initialRetryDelay: number;
    /** Maximum delay between reconnection attempts (ms) */
    maxRetryDelay: number;
    /** Heartbeat interval (ms) */
    heartbeatInterval: number;
    /** Heartbeat timeout (ms) */
    heartbeatTimeout: number;
    /** Inactivity timeout (ms) - 0 to disable */
    inactivityTimeout: number;
}

const DEFAULT_CONFIG: WebSocketConfig = {
    maxRetries: 10,
    initialRetryDelay: 1000,
    maxRetryDelay: 30000,
    heartbeatInterval: 30000,
    heartbeatTimeout: 10000,
    inactivityTimeout: 300000  // 5 minutes default
};

/**
 * Manages WebSocket connection with automatic reconnection and heartbeat.
 */
export class WebSocketManager {
    private ws: WebSocket | null = null;
    private serverUrl: string | null = null;
    private config: WebSocketConfig;
    private retryCount = 0;
    private retryTimeout: ReturnType<typeof setTimeout> | null = null;
    private heartbeatInterval: ReturnType<typeof setInterval> | null = null;
    private heartbeatTimeout: ReturnType<typeof setTimeout> | null = null;
    private lastActivityTime: number = Date.now();
    private messageQueue: string[] = [];
    private isConnecting = false;

    /** Callback when connection is established */
    public onOpen: (() => void) | null = null;
    /** Callback when connection is closed */
    public onClose: ((reason?: string) => void) | null = null;
    /** Callback when a message is received */
    public onMessage: ((data: unknown) => void) | null = null;
    /** Callback when an error occurs */
    public onError: ((error: Error) => void) | null = null;

    constructor(config: Partial<WebSocketConfig> = {}) {
        this.config = { ...DEFAULT_CONFIG, ...config };
    }

    /**
     * Update configuration options.
     * Only updates the provided options, keeping others unchanged.
     * @param config Partial configuration to merge
     */
    public setConfig(config: Partial<WebSocketConfig>): void {
        this.config = { ...this.config, ...config };
    }

    /**
     * Connect to the WebSocket server.
     * @param serverUrl The WebSocket server URL
     */
    public connect(serverUrl: string): void {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            // Already connected
            return;
        }

        if (this.isConnecting) {
            // Connection in progress
            return;
        }

        this.serverUrl = serverUrl;
        this.isConnecting = true;
        // Reset retry count since this is an explicit connect request
        // (e.g., from hot reload reconnection)
        this.retryCount = 0;
        this.createConnection();
    }

    /**
     * Disconnect from the WebSocket server.
     */
    public disconnect(): void {
        this.cleanup();
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.close(1000, 'Client disconnect');
        }
        this.ws = null;
        this.serverUrl = null;
        this.retryCount = 0;
    }

    /**
     * Send a message through the WebSocket connection.
     * If not connected, queues the message and triggers reconnection.
     * @param message The message to send
     */
    public send(message: unknown): void {
        const data = JSON.stringify(message);

        // Track activity for non-heartbeat messages
        const msgObj = message as { type?: string };
        if (msgObj.type !== 'heartbeat') {
            this.lastActivityTime = Date.now();
        }

        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(data);
        } else {
            // Queue message for when connection is established
            this.messageQueue.push(data);

            // Trigger reconnect if we have a server URL but aren't connected/connecting
            if (this.serverUrl && !this.isConnecting) {
                this.isConnecting = true;
                // Reset retry count since this is user-initiated activity
                this.retryCount = 0;
                this.createConnection();
            }
        }
    }

    /**
     * Check if the WebSocket is currently connected.
     */
    public get isConnected(): boolean {
        return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
    }

    private createConnection(): void {
        if (!this.serverUrl) {
            return;
        }

        try {
            this.ws = new WebSocket(this.serverUrl);
            this.ws.onopen = this.handleOpen.bind(this);
            this.ws.onclose = this.handleClose.bind(this);
            this.ws.onmessage = this.handleMessage.bind(this);
            this.ws.onerror = this.handleError.bind(this);
        } catch (error) {
            this.isConnecting = false;
            this.scheduleReconnect();
        }
    }

    private handleOpen(): void {
        this.isConnecting = false;
        this.retryCount = 0;
        this.lastActivityTime = Date.now();

        // Flush queued messages
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            if (message && this.ws) {
                this.ws.send(message);
            }
        }

        // Start heartbeat (also handles inactivity check)
        this.startHeartbeat();

        if (this.onOpen) {
            this.onOpen();
        }
    }

    private handleClose(event: CloseEvent): void {
        this.isConnecting = false;
        this.cleanup();

        const reason = event.reason || 'Connection closed';

        if (this.onClose) {
            this.onClose(reason);
        }

        // Only reconnect if:
        // - We haven't explicitly disconnected (code 1000)
        // - It's not an inactivity timeout (code 4001)
        if (this.serverUrl && event.code !== 1000 && event.code !== 4001) {
            this.scheduleReconnect();
        }
    }

    private handleMessage(event: MessageEvent): void {
        try {
            const data = JSON.parse(event.data);

            // Handle heartbeat acknowledgment - does NOT count as activity
            if (data.type === 'heartbeat_ack') {
                this.clearHeartbeatTimeout();
                return;
            }

            // Track activity for actual callback messages
            this.lastActivityTime = Date.now();

            if (this.onMessage) {
                this.onMessage(data);
            }
        } catch (error) {
            if (this.onError) {
                this.onError(new Error('Failed to parse message'));
            }
        }
    }

    private handleError(): void {
        this.isConnecting = false;
        // WebSocket error events don't contain useful information
        // The close event will follow with more details
    }

    private scheduleReconnect(): void {
        if (this.retryTimeout) {
            clearTimeout(this.retryTimeout);
        }

        if (this.retryCount >= this.config.maxRetries) {
            if (this.onError) {
                this.onError(new Error('Max reconnection attempts reached'));
            }
            return;
        }

        // Exponential backoff with jitter
        const delay = Math.min(
            this.config.initialRetryDelay * Math.pow(2, this.retryCount) +
                Math.random() * 1000,
            this.config.maxRetryDelay
        );

        this.retryCount++;

        this.retryTimeout = setTimeout(() => {
            this.createConnection();
        }, delay);
    }

    private startHeartbeat(): void {
        this.stopHeartbeat();

        this.heartbeatInterval = setInterval(() => {
            if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
                return;
            }

            // Check for inactivity timeout
            if (this.config.inactivityTimeout > 0) {
                const timeSinceActivity = Date.now() - this.lastActivityTime;
                if (timeSinceActivity >= this.config.inactivityTimeout) {
                    this.ws.close(4001, 'Inactivity timeout');
                    return;
                }
            }

            this.ws.send(JSON.stringify({ type: 'heartbeat' }));
            this.setHeartbeatTimeout();
        }, this.config.heartbeatInterval);
    }

    private stopHeartbeat(): void {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
        this.clearHeartbeatTimeout();
    }

    private setHeartbeatTimeout(): void {
        this.clearHeartbeatTimeout();

        this.heartbeatTimeout = setTimeout(() => {
            // Heartbeat timeout - connection may be dead
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.close(4000, 'Heartbeat timeout');
            }
        }, this.config.heartbeatTimeout);
    }

    private clearHeartbeatTimeout(): void {
        if (this.heartbeatTimeout) {
            clearTimeout(this.heartbeatTimeout);
            this.heartbeatTimeout = null;
        }
    }

    private cleanup(): void {
        this.stopHeartbeat();
        if (this.retryTimeout) {
            clearTimeout(this.retryTimeout);
            this.retryTimeout = null;
        }
    }
}
