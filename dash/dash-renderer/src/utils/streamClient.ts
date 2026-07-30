/**
 * Single multiplexed streaming transport for the page.
 *
 * Instead of one long-lived NDJSON connection per streaming callback (which hits
 * the browser's ~6-connections-per-host ceiling), every streaming callback shares
 * ONE downlink connection. A callback POSTs its request (which returns a fast ack)
 * carrying a connection id + request id; the server pumps that callback's frames
 * onto the connection's shared-storage topic; the single downlink relays them and
 * this client routes each frame back to the right callback by request id.
 *
 * Lifecycle: the downlink opens on the first streaming callback and closes once no
 * callbacks remain in flight ("collect the dones to match the runnings"). If it
 * drops while callbacks are still running it reconnects, resuming from the last
 * sequence it saw so buffered frames are replayed rather than lost.
 *
 * This currently runs on the page; it is written to be host-agnostic so it can
 * move into a SharedWorker (one connection per browser, shared across tabs) later.
 */

type Frame = Record<string, any>;

interface PendingStream {
    onFrame: (frame: Frame) => void;
    resolve: () => void;
    reject: (err: Error) => void;
}

interface DownlinkEnvelope {
    rid: string;
    frame: Frame;
    seq?: number;
}

type FetchImpl = typeof fetch;

const genId = (): string =>
    `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;

const sleep = (ms: number): Promise<void> =>
    new Promise(resolve => setTimeout(resolve, ms));

export class StreamClient {
    private connectionId = genId();
    private pending = new Map<string, PendingStream>();
    private counter = 0;
    // Last sequence applied; the downlink resumes from here on reconnect. Starts
    // at 0 so the first connect replays anything published before it subscribed
    // (the uplink POST and the downlink open race).
    private cursor = 0;
    private downlinkOpen = false;
    private abort: AbortController | null = null;
    private reconnectDelay: number;
    private fetchImpl: FetchImpl;

    constructor(opts: {fetchImpl?: FetchImpl; reconnectDelay?: number} = {}) {
        this.fetchImpl = opts.fetchImpl ?? fetch;
        this.reconnectDelay = opts.reconnectDelay ?? 1000;
    }

    get activeCount(): number {
        return this.pending.size;
    }

    /**
     * Run one streaming callback over the multiplexed transport. Resolves when
     * the callback's terminal `done` frame arrives (its output frames having
     * been delivered to `onFrame` as they arrive), or rejects on error.
     */
    run(
        url: string,
        init: RequestInit,
        payload: Record<string, any>,
        onFrame: (frame: Frame) => void
    ): Promise<void> {
        const requestId = `${this.connectionId}-${++this.counter}`;
        const settled = new Promise<void>((resolve, reject) => {
            this.pending.set(requestId, {onFrame, resolve, reject});
        });
        this.ensureDownlink(url, init);
        // Uplink POST: returns a fast ack; the outputs arrive on the downlink.
        this.fetchImpl(url, {
            ...init,
            method: 'POST',
            body: JSON.stringify({
                ...payload,
                streamConnection: {connectionId: this.connectionId, requestId}
            })
        }).catch(err => this.fail(requestId, err));
        return settled;
    }

    /** Route one downlink envelope to its callback. Public for testing. */
    dispatchEnvelope(envelope: DownlinkEnvelope): void {
        if (typeof envelope.seq === 'number') {
            this.cursor = envelope.seq;
        }
        const pending = this.pending.get(envelope.rid);
        if (!pending) {
            // A frame for a callback we already resolved (e.g. a replayed
            // duplicate after reconnect) -- safe to drop.
            return;
        }
        const {frame} = envelope;
        if (frame.done) {
            this.pending.delete(envelope.rid);
            if (frame.error) {
                pending.reject(
                    new Error(frame.error.message || 'Streaming callback error')
                );
            } else {
                pending.resolve();
            }
            this.stopDownlinkIfIdle();
        } else {
            pending.onFrame(frame);
        }
    }

    private fail(requestId: string, err: Error): void {
        const pending = this.pending.get(requestId);
        if (pending) {
            this.pending.delete(requestId);
            pending.reject(err);
            this.stopDownlinkIfIdle();
        }
    }

    private stopDownlinkIfIdle(): void {
        if (this.pending.size === 0 && this.abort) {
            this.abort.abort(); // ends the read loop; downlink closes
        }
    }

    private ensureDownlink(url: string, init: RequestInit): void {
        if (this.downlinkOpen) {
            return;
        }
        this.downlinkOpen = true;
        // Fire-and-forget read loop; it exits when no callbacks remain.
        this.readLoop(url, init).finally(() => {
            this.downlinkOpen = false;
            this.abort = null;
        });
    }

    private async readLoop(url: string, init: RequestInit): Promise<void> {
        while (this.pending.size > 0) {
            this.abort = new AbortController();
            try {
                const res = await this.fetchImpl(url, {
                    ...init,
                    method: 'POST',
                    signal: this.abort.signal,
                    body: JSON.stringify({
                        streamDownlink: {
                            connectionId: this.connectionId,
                            from: this.cursor
                        }
                    })
                });
                if (!res.ok || !res.body) {
                    throw new Error(`downlink responded ${res.status}`);
                }
                await this.consume(res.body);
            } catch (err) {
                if (this.pending.size === 0) {
                    break; // deliberately aborted because we went idle
                }
                // Genuine drop with work outstanding: reconnect from the cursor.
                await sleep(this.reconnectDelay);
            }
        }
    }

    private async consume(body: ReadableStream<Uint8Array>): Promise<void> {
        const reader = body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        for (;;) {
            const {done, value} = await reader.read();
            if (done) {
                return; // connection ended -> reconnect via the read loop
            }
            buffer += decoder.decode(value, {stream: true});
            let nl: number;
            while ((nl = buffer.indexOf('\n')) >= 0) {
                const line = buffer.slice(0, nl);
                buffer = buffer.slice(nl + 1);
                if (!line.trim()) {
                    continue; // keepalive blank line
                }
                this.dispatchEnvelope(JSON.parse(line));
            }
        }
    }
}

let singleton: StreamClient | null = null;

export function getStreamClient(): StreamClient {
    if (!singleton) {
        singleton = new StreamClient();
    }
    return singleton;
}
