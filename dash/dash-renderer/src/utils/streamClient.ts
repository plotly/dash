/**
 * Multiplexed streaming transport for streaming callbacks.
 *
 * Instead of one long-lived NDJSON connection per streaming callback (which hits
 * the browser's ~6-connections-per-host ceiling), every streaming callback shares
 * ONE downlink connection. A callback POSTs its request (which returns a fast ack)
 * carrying a request id; the server pumps that callback's frames onto the
 * connection's shared-storage topic; the single downlink relays them and the
 * client routes each frame back to the right callback by request id.
 *
 * The connection is keyed server-side on the page's signed endId (sent as a query
 * parameter on every uplink, downlink and cancel), never on anything the client
 * picks, so a page can only ever read or write its own topic.
 *
 * Two hosts run this transport:
 *
 * - `StreamClient` owns the HTTP side: the uplink POSTs and the downlink read
 *   loop. It runs inside the page when no worker is available.
 * - `SharedStreamClient` is the page's proxy to a `StreamClient` hosted in a
 *   SharedWorker (`workers/streamWorker.ts`), so every tab of the browser shares
 *   one downlink -- the per-host connection cap is shared across tabs, and a
 *   downlink per tab stalls the sixth tab. The worker pins the endId of the
 *   first tab that streams for as long as the connection has streams in
 *   flight, keeps the downlink open while any tab has a stream, and cancels a
 *   tab's streams server-side when that tab goes away.
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
 * Lifecycle: the downlink opens once the first uplink is acknowledged and closes
 * when no acknowledged callback remains in flight ("collect the dones to match
 * the runnings"). Waiting for the ack lets a single request slot serve the two
 * in turn; frames published before the downlink subscribes are replayed from
 * the cursor. If the downlink drops while callbacks are still running it
 * reconnects, resuming from the last sequence it saw, backing off until the
 * server has been unreachable for the whole reconnect window.
 */

import {getRendererId} from './rendererId';

type Frame = Record<string, any>;

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
// half second at about four polls per frame instead of ten; the cap bounds
// the latency of a slow stream's next frame so consecutive frames still
// render one at a time instead of bunching into one poll.
const EMPTY_POLLS_BEFORE_BACKOFF = 2;
const MAX_BACKOFF_FACTOR = 5;

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
        endId: string,
        payload: Record<string, any>,
        onFrame: (frame: Frame) => void
    ): Promise<void>;
}

interface PendingStream {
    onFrame: (frame: Frame) => void;
    resolve: () => void;
    reject: (err: Error) => void;
    // Whether the uplink POST was acknowledged; only acknowledged callbacks
    // keep the downlink open (see the lifecycle note above).
    acked: boolean;
    // Whether any output frame reached this callback. Decides how a lost
    // connection settles it: frames applied -> resolve and keep them (like the
    // single-connection NDJSON path does on a drop); nothing applied -> reject,
    // so the caller can report it or fall back.
    gotFrame: boolean;
}

interface DownlinkEnvelope {
    rid?: string;
    frame?: Frame;
    seq?: number;
    // Set by the server when this connection's buffered frames were lost (its
    // owner was re-elected, or the server restarted): the client must reset its
    // cursor to the head rather than keep asking to resume from a stale one.
    reset?: boolean;
}

type FetchImpl = typeof fetch;

const genId = (): string =>
    `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;

const sleep = (ms: number): Promise<void> =>
    new Promise(resolve => setTimeout(resolve, ms));

export class StreamClient implements StreamTransport {
    // Local id, used only to make request ids unique on this host. The server
    // does NOT key the topic on it: the connection is keyed on the signed endId
    // instead, so a client can't name another page's topic. See streamUrl.
    private localId = genId();
    // The endId this connection is keyed on. Pinned by the first stream and
    // kept while any stream is in flight, so every tab behind a shared worker
    // publishes to and reads from the same topic.
    private endId = '';
    private pending = new Map<string, PendingStream>();
    private counter = 0;
    // Last sequence applied; the downlink resumes from here on reconnect. Starts
    // at 0 so the first connect replays anything published before it subscribed
    // (the uplink POST and the downlink open race).
    private cursor = 0;
    private downlinkOpen = false;
    private abort: AbortController | null = null;
    // Bumped whenever a read loop starts or the downlink is closed, so a
    // retired loop (closed while it was mid-await) notices and exits instead
    // of fighting a newer loop for the connection.
    private loopGen = 0;
    private reconnectDelay: number;
    private maxReconnectDelay: number;
    private reconnectWindow: number;
    private fetchImpl: FetchImpl;
    private _transport: StreamTransportOptions = {};
    // Resolves the current idle pause early (a new stream started).
    private wakeUp: (() => void) | null = null;
    // Set by start(): the read loop resets its idle backoff on the next turn.
    private wokenForNewStream = false;

    constructor(
        opts: {
            fetchImpl?: FetchImpl;
            // First retry delay after a downlink drop; doubles up to
            // maxReconnectDelay on each further failure.
            reconnectDelay?: number;
            maxReconnectDelay?: number;
            // How long the downlink may stay unreachable before the callbacks
            // waiting on it are settled as lost instead of retrying forever.
            reconnectWindow?: number;
        } & StreamTransportOptions = {}
    ) {
        // Native fetch must be invoked with `this === window`; calling it as a
        // method of this object throws "Illegal invocation", so bind it.
        // globalThis is window on a page and self in a worker.
        this.fetchImpl = opts.fetchImpl ?? fetch.bind(globalThis);
        this.reconnectDelay = opts.reconnectDelay ?? 1000;
        this.maxReconnectDelay = opts.maxReconnectDelay ?? 5000;
        this.reconnectWindow = opts.reconnectWindow ?? 30000;
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

    /** The endId this connection is currently keyed on (empty when idle). */
    get connectionEndId(): string {
        return this.endId;
    }

    /** Append the signed endId so the server can derive (and authorize) the
     * connection topic. The server never trusts a client-supplied topic id. */
    private streamUrl(url: string): string {
        if (!this.endId) {
            return url;
        }
        const delim = url.includes('?') ? '&' : '?';
        return `${url}${delim}endId=${encodeURIComponent(this.endId)}`;
    }

    run(
        url: string,
        init: RequestInit,
        endId: string,
        payload: Record<string, any>,
        onFrame: (frame: Frame) => void
    ): Promise<void> {
        return this.start(url, init, endId, payload, onFrame).settled;
    }

    /**
     * `run`, also handing back the request id so the caller can `cancel` the
     * stream later (the worker host does, for a tab that went away).
     */
    start(
        url: string,
        init: RequestInit,
        endId: string,
        payload: Record<string, any>,
        onFrame: (frame: Frame) => void
    ): {requestId: string; settled: Promise<void>} {
        if (this.pending.size === 0 || !this.endId) {
            // Nothing in flight: this stream's page keys the connection. While
            // streams are in flight the key stays put, so a stream from
            // another tab (shared worker) lands on the same topic.
            this.endId = endId || '';
        }
        const requestId = `${this.localId}-${++this.counter}`;
        const settled = new Promise<void>((resolve, reject) => {
            this.pending.set(requestId, {
                onFrame,
                resolve,
                reject,
                acked: false,
                gotFrame: false
            });
        });
        // Uplink POST: returns a fast ack; the outputs arrive on the downlink,
        // which opens once the ack is in.
        this.fetchImpl(this.streamUrl(url), {
            ...init,
            method: 'POST',
            body: JSON.stringify({
                ...payload,
                streamConnection: {requestId}
            })
        })
            .then(res => this.checkUplink(requestId, res, url, init))
            .catch(err => this.fail(requestId, err));
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
        this.fetchImpl(this.streamUrl(url), {
            ...init,
            method: 'POST',
            body: JSON.stringify({streamCancel: {requestId}})
        }).catch(() => undefined);
        this.stopDownlinkIfIdle();
    }

    /**
     * The uplink returns a fast ack (200); the frames then arrive on the
     * downlink, so make sure one is open. Any non-ok status (e.g. 403 when the
     * connection did not verify) means no frames are coming, so fail the
     * request loudly rather than leave the callback pending forever.
     */
    private checkUplink(
        requestId: string,
        res: Response,
        url: string,
        init: RequestInit
    ): void {
        if (!res.ok) {
            this.fail(
                requestId,
                new Error(`stream uplink responded ${res.status}`)
            );
            return;
        }
        const pending = this.pending.get(requestId);
        if (pending) {
            pending.acked = true;
            this.ensureDownlink(url, init);
            // A polling downlink may be pausing between polls: this stream's
            // first frame should not wait out that pause.
            this.wokenForNewStream = true;
            this.wakeUp?.();
        }
    }

    /** Whether any acknowledged callback is still waiting on the downlink. */
    private hasAcked(): boolean {
        for (const p of this.pending.values()) {
            if (p.acked) {
                return true;
            }
        }
        return false;
    }

    /** Route one downlink envelope to its callback. Public for testing. */
    dispatchEnvelope(envelope: DownlinkEnvelope): void {
        if (envelope.reset) {
            // Our cursor points into a server incarnation that lost our frames
            // (it restarted, or the storage owner changed). Reset to the head so
            // a later downlink starts from what the fresh topic actually has,
            // and settle the callbacks in flight: the frames they were waiting
            // on are gone, and after a restart nothing will ever finish them.
            this.cursor = 0;
            this.settleAll(
                new Error(
                    'stream reset: the server lost this connection (restart or owner change)'
                )
            );
            return;
        }
        if (typeof envelope.seq === 'number') {
            this.cursor = envelope.seq;
        }
        if (envelope.rid === undefined || envelope.frame === undefined) {
            return;
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
            pending.gotFrame = true;
            pending.onFrame(frame);
        }
    }

    /**
     * The downlink is gone for good (refused by the server, reset, or
     * unreachable past the reconnect window). Callbacks that already applied
     * frames resolve so those frames stay on the page; ones that never got a
     * frame reject with `err`, and the read loop winds down since nothing is
     * pending any more.
     */
    private settleAll(err: Error): void {
        const pending = Array.from(this.pending.values());
        this.pending.clear();
        // Close before settling: a continuation of a settled promise may start
        // a new stream right away, and it must get a fresh downlink rather
        // than find this one still marked open.
        this.closeDownlink();
        pending.forEach(p => (p.gotFrame ? p.resolve() : p.reject(err)));
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
        if (this.downlinkOpen && !this.hasAcked()) {
            this.closeDownlink();
        }
    }

    /** Retire the current read loop and end its connection. */
    private closeDownlink(): void {
        const abort = this.abort;
        this.abort = null;
        this.downlinkOpen = false;
        this.loopGen++;
        this.wakeUp?.();
        if (abort) {
            abort.abort();
        }
    }

    private ensureDownlink(url: string, init: RequestInit): void {
        if (this.downlinkOpen) {
            return;
        }
        this.downlinkOpen = true;
        // Fire-and-forget read loop; it exits when no callbacks remain.
        this.readLoop(url, init, ++this.loopGen);
    }

    private async readLoop(
        url: string,
        init: RequestInit,
        gen: number
    ): Promise<void> {
        const polling = this._transport.mode === 'poll';
        const base = this._transport.pollInterval ?? DEFAULT_POLL_INTERVAL;
        let idlePause = base;
        let emptyPolls = 0;
        let unreachableSince: number | null = null;
        let delay = this.reconnectDelay;
        while (this.hasAcked() && this.loopGen === gen) {
            if (this.wokenForNewStream) {
                this.wokenForNewStream = false;
                emptyPolls = 0;
                idlePause = base;
            }
            this.abort = new AbortController();
            let received = 0;
            try {
                const res = await this.fetchImpl(this.streamUrl(url), {
                    ...init,
                    method: 'POST',
                    signal: this.abort.signal,
                    body: JSON.stringify({
                        streamDownlink: {from: this.cursor}
                    })
                });
                if (res.status >= 400 && res.status < 500) {
                    // The server refuses this connection outright, typically
                    // 403 after a restart minted a new signing secret so our
                    // endId no longer verifies. Retrying cannot fix that.
                    this.settleAll(
                        new Error(`stream downlink responded ${res.status}`)
                    );
                    break;
                }
                if (!res.ok || !res.body) {
                    throw new Error(`downlink responded ${res.status}`);
                }
                received = await this.consume(res.body);
                if (received === 0 && !polling) {
                    // Accepted then closed without a single envelope (a server
                    // mid-shutdown, a proxy dropping idle connections): back
                    // off like a failure instead of reconnecting in a burst.
                    throw new Error('downlink closed without data');
                }
                // A productive connection ended (proxy timeout, worker
                // recycle) or a poll completed: fresh backoff.
                unreachableSince = null;
                delay = this.reconnectDelay;
            } catch (err) {
                if (!this.hasAcked() || this.loopGen !== gen) {
                    break; // closed on purpose: idle, or settled and retired
                }
                // Genuine drop with work outstanding: reconnect from the
                // cursor, backing off, until the server has been unreachable
                // for the whole window. Past that the callbacks are lost.
                const now = Date.now();
                unreachableSince = unreachableSince ?? now;
                if (now - unreachableSince >= this.reconnectWindow) {
                    this.settleAll(
                        new Error(
                            'stream downlink lost: could not reconnect to the server'
                        )
                    );
                    break;
                }
                await sleep(delay);
                delay = Math.min(delay * 2, this.maxReconnectDelay);
                continue;
            }
            if (polling && this.hasAcked() && this.loopGen === gen) {
                // The response was one poll. Frames came: poll again soon.
                // Nothing came: keep the pace for a few polls, then back off
                // up to a bound, until frames or a new stream wake us.
                if (received) {
                    emptyPolls = 0;
                    idlePause = base;
                } else if (++emptyPolls > EMPTY_POLLS_BEFORE_BACKOFF) {
                    idlePause = Math.min(
                        idlePause * 2,
                        base * MAX_BACKOFF_FACTOR
                    );
                }
                await this.pause(idlePause);
            }
        }
        if (this.loopGen === gen) {
            this.downlinkOpen = false;
            this.abort = null;
        }
    }

    /** Sleep for `ms`, or until a new stream starts or the downlink closes. */
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

    /** Relay envelopes until the connection ends; returns how many arrived. */
    private async consume(body: ReadableStream<Uint8Array>): Promise<number> {
        const reader = body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let received = 0;
        for (;;) {
            const {done, value} = await reader.read();
            if (done) {
                return received; // connection ended -> the read loop decides
            }
            buffer += decoder.decode(value, {stream: true});
            let nl: number;
            while ((nl = buffer.indexOf('\n')) >= 0) {
                const line = buffer.slice(0, nl);
                buffer = buffer.slice(nl + 1);
                if (!line.trim()) {
                    continue; // keepalive blank line
                }
                received++;
                this.dispatchEnvelope(JSON.parse(line));
            }
        }
    }
}

// --- SharedWorker host ------------------------------------------------------
//
// Messages page -> worker:
//   {type: 'stream', rendererId, requestId, url, init, endId, payload, transport}
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
          // The page's signed endId; the first tab's keys the connection.
          endId: string;
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
        endId: string,
        payload: Record<string, any>,
        onFrame: (frame: Frame) => void
    ): Promise<void> {
        const requestId = `${this.rendererId}-${++this.counter}`;
        return new Promise<void>((resolve, reject) => {
            this.pending.set(requestId, {
                onFrame,
                resolve,
                reject,
                acked: false,
                gotFrame: false
            });
            const message: StreamHostMessage = {
                type: 'stream',
                rendererId: this.rendererId,
                requestId,
                url,
                init,
                endId: endId || '',
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
