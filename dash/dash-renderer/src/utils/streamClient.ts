/**
 * Multiplexed streaming transport for streaming callbacks.
 *
 * Instead of one long-lived NDJSON connection per streaming callback (which hits
 * the browser's ~6-connections-per-host ceiling), every streaming callback shares
 * ONE downlink connection. A callback POSTs its request (which returns a fast ack)
 * carrying a connection id + request id; the server pumps that callback's frames
 * onto the connection's shared-storage topic; the single downlink relays them and
 * the client routes each frame back to the right callback by request id.
 *
 * Two hosts run this transport:
 *
 * - `StreamClient` owns the HTTP side: the uplink POSTs and the downlink read
 *   loop. It runs inside the page when no worker is available.
 * - `SharedStreamClient` is the page's proxy to a `StreamClient` hosted in a
 *   SharedWorker (`workers/streamWorker.ts`), so every tab of the browser shares
 *   one downlink -- the per-host connection cap is shared across tabs, and a
 *   downlink per tab stalls the sixth tab. The worker keeps the downlink open as
 *   long as any tab has a stream in flight and cancels a tab's streams server-side
 *   when that tab goes away.
 *
 * Two downlink modes, chosen by the server (config.stream.mode):
 *
 * - 'stream' (ASGI): one long-lived NDJSON response; frames arrive as produced.
 * - 'poll' (WSGI): each downlink request returns the frames queued since the
 *   cursor and ends at once, so it holds a server worker thread for
 *   milliseconds rather than for the whole visit. The client re-polls after
 *   `pollInterval` while frames keep coming, backs off to ten times that while
 *   quiet, and polls immediately when a new stream starts.
 *
 * Lifecycle: the downlink opens on the first streaming callback and closes once no
 * callbacks remain in flight ("collect the dones to match the runnings"). If it
 * drops while callbacks are still running it reconnects, resuming from the last
 * sequence it saw so buffered frames are replayed rather than lost.
 */

import {getRendererId} from './rendererId';

type Frame = Record<string, any>;

/** What the callbacks action needs from either host. */
export interface StreamTransport {
    /**
     * Run one streaming callback. Resolves when the callback's terminal `done`
     * frame arrives (its output frames having been delivered to `onFrame` as
     * they arrive), or rejects on error.
     */
    run(
        url: string,
        init: RequestInit,
        payload: Record<string, any>,
        onFrame: (frame: Frame) => void
    ): Promise<void>;
}

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

/** How the server serves the downlink; see the module comment. */
export interface StreamTransportOptions {
    mode?: 'stream' | 'poll';
    /** Poll mode: delay between polls while frames flow, in ms (default 100). */
    pollInterval?: number;
}

const DEFAULT_POLL_INTERVAL = 100;
// Idle polls stay at the interval for this many empty polls (a callback's
// next frame is usually moments away), then back off geometrically up to
// MAX_BACKOFF_FACTOR times the interval. Two keeps a stream that yields every
// half second at about four polls per frame instead of ten.
const EMPTY_POLLS_BEFORE_BACKOFF = 2;
const MAX_BACKOFF_FACTOR = 10;

const genId = (): string =>
    `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;

const sleep = (ms: number): Promise<void> =>
    new Promise(resolve => setTimeout(resolve, ms));

export class StreamClient implements StreamTransport {
    readonly connectionId = genId();
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
    private _transport: StreamTransportOptions = {};
    // Resolves the current idle pause early (a new stream started).
    private wakeUp: (() => void) | null = null;
    // Set by start(): the read loop resets its idle backoff on the next turn.
    private wokenForNewStream = false;

    constructor(
        opts: {
            fetchImpl?: FetchImpl;
            reconnectDelay?: number;
        } & StreamTransportOptions = {}
    ) {
        // Native fetch must be invoked with `this === window`; calling it as a
        // method of this object throws "Illegal invocation", so bind it.
        // globalThis is window on a page and self in a worker.
        this.fetchImpl = opts.fetchImpl ?? fetch.bind(globalThis);
        this.reconnectDelay = opts.reconnectDelay ?? 1000;
        this.configure(opts);
    }

    /** Adopt the server's downlink mode (the worker host learns it from the page). */
    configure(transport: StreamTransportOptions): void {
        if (transport.mode) {
            this._transport.mode = transport.mode;
        }
        if (typeof transport.pollInterval === 'number') {
            this._transport.pollInterval = transport.pollInterval;
        }
    }

    get transport(): StreamTransportOptions {
        return {...this._transport};
    }

    get activeCount(): number {
        return this.pending.size;
    }

    run(
        url: string,
        init: RequestInit,
        payload: Record<string, any>,
        onFrame: (frame: Frame) => void
    ): Promise<void> {
        return this.start(url, init, payload, onFrame).settled;
    }

    /**
     * `run`, also handing back the request id so the caller can `cancel` the
     * stream later (the worker host does, for a tab that went away).
     */
    start(
        url: string,
        init: RequestInit,
        payload: Record<string, any>,
        onFrame: (frame: Frame) => void
    ): {requestId: string; settled: Promise<void>} {
        const requestId = `${this.connectionId}-${++this.counter}`;
        const settled = new Promise<void>((resolve, reject) => {
            this.pending.set(requestId, {onFrame, resolve, reject});
        });
        this.ensureDownlink(url, init);
        // A polling downlink may be pausing between polls: its first frame
        // should not wait out that pause.
        this.wakeUp?.();
        this.wokenForNewStream = true;
        // Uplink POST: returns a fast ack; the outputs arrive on the downlink.
        this.fetchImpl(url, {
            ...init,
            method: 'POST',
            body: JSON.stringify({
                ...payload,
                streamConnection: {connectionId: this.connectionId, requestId}
            })
        }).catch(err => this.fail(requestId, err));
        return {requestId, settled};
    }

    /**
     * Abandon one in-flight callback whose consumer is gone: stop waiting for
     * its frames (they are dropped on arrival) and tell the server to cancel
     * it, so it does not run to completion for nobody. Its promise rejects.
     */
    cancel(requestId: string, url: string, init: RequestInit): void {
        const pending = this.pending.get(requestId);
        if (!pending) {
            return;
        }
        this.pending.delete(requestId);
        pending.reject(new Error('Streaming callback cancelled'));
        this.fetchImpl(url, {
            ...init,
            method: 'POST',
            body: JSON.stringify({
                streamCancel: {connectionId: this.connectionId, requestId}
            })
        }).catch(() => undefined);
        this.stopDownlinkIfIdle();
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
        const base = this._transport.pollInterval ?? DEFAULT_POLL_INTERVAL;
        let idlePause = base;
        let emptyPolls = 0;
        while (this.pending.size > 0) {
            if (this.wokenForNewStream) {
                this.wokenForNewStream = false;
                emptyPolls = 0;
                idlePause = base;
            }
            this.abort = new AbortController();
            let delivered = 0;
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
                delivered = await this.consume(res.body);
            } catch (err) {
                if (this.pending.size === 0) {
                    break; // deliberately aborted because we went idle
                }
                // Genuine drop with work outstanding: reconnect from the cursor.
                await sleep(this.reconnectDelay);
                continue;
            }
            if (this.pending.size === 0) {
                break;
            }
            if (this._transport.mode === 'poll') {
                // The response was one poll. Frames came: poll again soon.
                // Nothing came: keep the pace for a few polls, then back off
                // up to a bound, until frames or a new stream wake us.
                if (delivered) {
                    emptyPolls = 0;
                    idlePause = base;
                } else if (++emptyPolls > EMPTY_POLLS_BEFORE_BACKOFF) {
                    idlePause = Math.min(
                        idlePause * 2,
                        base * MAX_BACKOFF_FACTOR
                    );
                }
                await this.pause(idlePause);
            } else if (!delivered) {
                // Stream mode: the server closed an open downlink without
                // sending anything (shutting down, or misconfigured to end
                // responses at once). Reconnect from the cursor, but never in
                // a hot loop.
                await sleep(this.reconnectDelay);
            }
            // Stream mode after frames: the connection ended mid-stream (a
            // drop with a clean close); reconnect at once from the cursor.
        }
    }

    /** Sleep for `ms`, or until a new stream starts (`wakeUp`). */
    private pause(ms: number): Promise<void> {
        return new Promise<void>(resolve => {
            const timer = setTimeout(() => {
                this.wakeUp = null;
                resolve();
            }, ms);
            this.wakeUp = () => {
                clearTimeout(timer);
                this.wakeUp = null;
                resolve();
            };
        });
    }

    /** Relay a downlink body; returns how many envelopes it carried. */
    private async consume(body: ReadableStream<Uint8Array>): Promise<number> {
        const reader = body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let delivered = 0;
        for (;;) {
            const {done, value} = await reader.read();
            if (done) {
                return delivered; // response ended -> the read loop decides
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
                delivered += 1;
            }
        }
    }
}

// --- SharedWorker host ------------------------------------------------------
//
// Messages page -> worker:
//   {type: 'stream', rendererId, requestId, url, init, payload, transport}
//   {type: 'unregister', rendererId}          this tab is going away
// Messages worker -> page:
//   {type: 'frame', requestId, frame}
//   {type: 'done', requestId}
//   {type: 'error', requestId, message}

export type StreamHostMessage =
    | {
          type: 'stream';
          rendererId: string;
          requestId: string;
          url: string;
          init: RequestInit;
          payload: Record<string, any>;
          // The server's downlink mode, from the page's config: the worker
          // has no config of its own.
          transport?: StreamTransportOptions;
      }
    | {type: 'unregister'; rendererId: string};

export type StreamPortMessage =
    | {type: 'frame'; requestId: string; frame: Frame}
    | {type: 'done'; requestId: string}
    | {type: 'error'; requestId: string; message: string};

/** The slice of MessagePort both sides use (fakeable in tests). */
export interface StreamPort {
    postMessage(message: any): void;
    onmessage: ((event: MessageEvent) => void) | null;
    start?(): void;
}

/**
 * The page's end of the SharedWorker transport: forwards each stream to the
 * worker and routes its frames back to the callback that started it.
 */
export class SharedStreamClient implements StreamTransport {
    private pending = new Map<string, PendingStream>();
    private counter = 0;
    private port: StreamPort;
    private rendererId: string;
    private transport: StreamTransportOptions;
    private _broken = false;

    constructor(
        port: StreamPort,
        rendererId: string = getRendererId(),
        transport: StreamTransportOptions = {}
    ) {
        this.port = port;
        this.rendererId = rendererId;
        this.transport = transport;
        port.onmessage = event => this.handleMessage(event.data);
        port.start?.();
    }

    /** True once the worker failed; callers should fall back to `StreamClient`. */
    get broken(): boolean {
        return this._broken;
    }

    get activeCount(): number {
        return this.pending.size;
    }

    run(
        url: string,
        init: RequestInit,
        payload: Record<string, any>,
        onFrame: (frame: Frame) => void
    ): Promise<void> {
        const requestId = `${this.rendererId}-${++this.counter}`;
        return new Promise<void>((resolve, reject) => {
            this.pending.set(requestId, {onFrame, resolve, reject});
            const message: StreamHostMessage = {
                type: 'stream',
                rendererId: this.rendererId,
                requestId,
                url,
                init,
                payload,
                transport: this.transport
            };
            this.port.postMessage(message);
        });
    }

    /**
     * This tab is going away (pagehide): its streams have no consumer any
     * more, so the worker cancels them server-side.
     */
    release(): void {
        const message: StreamHostMessage = {
            type: 'unregister',
            rendererId: this.rendererId
        };
        this.port.postMessage(message);
    }

    /** The worker died or failed to load: reject everything in flight. */
    fail(err: Error): void {
        this._broken = true;
        for (const pending of this.pending.values()) {
            pending.reject(err);
        }
        this.pending.clear();
    }

    private handleMessage(message: StreamPortMessage): void {
        const pending = this.pending.get(message.requestId);
        if (!pending) {
            return;
        }
        if (message.type === 'frame') {
            pending.onFrame(message.frame);
            return;
        }
        this.pending.delete(message.requestId);
        if (message.type === 'done') {
            pending.resolve();
        } else {
            pending.reject(new Error(message.message));
        }
    }
}

let singleton: StreamTransport | null = null;

/**
 * The page's streaming transport: the SharedWorker-hosted downlink when the
 * server provides the worker script and the browser supports SharedWorker,
 * otherwise a downlink of the page's own.
 */
export function getStreamClient(
    config: {
        stream?: {
            worker_url?: string;
            mode?: 'stream' | 'poll';
            poll_interval?: number;
        };
    } = {}
): StreamTransport {
    if (singleton instanceof SharedStreamClient && singleton.broken) {
        singleton = null;
    }
    if (singleton) {
        return singleton;
    }
    const transport: StreamTransportOptions = {
        mode: config.stream?.mode,
        pollInterval: config.stream?.poll_interval
    };
    const workerUrl = config.stream?.worker_url;
    if (workerUrl && typeof SharedWorker !== 'undefined') {
        try {
            const worker = new SharedWorker(workerUrl, {
                name: 'dash-stream-worker'
            });
            const client = new SharedStreamClient(
                worker.port,
                getRendererId(),
                transport
            );
            worker.onerror = () =>
                client.fail(new Error('Dash stream worker failed'));
            window.addEventListener('pagehide', () => client.release());
            singleton = client;
            return singleton;
        } catch (err) {
            // Fall through to the in-page transport.
        }
    }
    singleton = new StreamClient(transport);
    return singleton;
}

/**
 * Whether the server offers the multiplexed streaming transport (i.e. it has a
 * shared-storage backend). When false, streaming callbacks fall back to one
 * NDJSON connection each.
 */
export function isStreamMultiplexed(config: {
    stream?: {enabled?: boolean};
}): boolean {
    return !!config.stream?.enabled;
}
