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

export class StreamClient {
    // Local id, used only to make request ids unique on this page. The server
    // does NOT key the topic on it: the connection is keyed on the signed endId
    // instead, so a client can't name another page's topic. See streamUrl.
    private localId = genId();
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
        } = {}
    ) {
        // Native fetch must be invoked with `this === window`; calling it as a
        // method of this object throws "Illegal invocation", so bind it.
        // globalThis is window on a page and self in a worker.
        this.fetchImpl = opts.fetchImpl ?? fetch.bind(globalThis);
        this.reconnectDelay = opts.reconnectDelay ?? 1000;
        this.maxReconnectDelay = opts.maxReconnectDelay ?? 5000;
        this.reconnectWindow = opts.reconnectWindow ?? 30000;
    }

    get activeCount(): number {
        return this.pending.size;
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

    /**
     * Run one streaming callback over the multiplexed transport. Resolves when
     * the callback's terminal `done` frame arrives (its output frames having
     * been delivered to `onFrame` as they arrive), or rejects on error.
     */
    run(
        url: string,
        init: RequestInit,
        endId: string,
        payload: Record<string, any>,
        onFrame: (frame: Frame) => void
    ): Promise<void> {
        this.endId = endId || '';
        const requestId = `${this.localId}-${++this.counter}`;
        const settled = new Promise<void>((resolve, reject) => {
            this.pending.set(requestId, {
                onFrame,
                resolve,
                reject,
                gotFrame: false
            });
        });
        this.ensureDownlink(url, init);
        // Uplink POST: returns a fast ack; the outputs arrive on the downlink.
        this.fetchImpl(this.streamUrl(url), {
            ...init,
            method: 'POST',
            body: JSON.stringify({
                ...payload,
                streamConnection: {requestId}
            })
        })
            .then(res => this.checkUplink(requestId, res))
            .catch(err => this.fail(requestId, err));
        return settled;
    }

    /**
     * The uplink returns a fast ack (200); the frames then arrive on the
     * downlink. Any non-ok status (e.g. 403 when the connection did not verify)
     * means no frames are coming, so fail the request loudly rather than leave
     * the callback pending forever.
     */
    private checkUplink(requestId: string, res: Response): void {
        if (!res.ok) {
            this.fail(
                requestId,
                new Error(`stream uplink responded ${res.status}`)
            );
        }
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
        if (this.pending.size === 0 && this.downlinkOpen) {
            this.closeDownlink();
        }
    }

    /** Retire the current read loop and end its connection. */
    private closeDownlink(): void {
        const abort = this.abort;
        this.abort = null;
        this.downlinkOpen = false;
        this.loopGen++;
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
        let unreachableSince: number | null = null;
        let delay = this.reconnectDelay;
        while (this.pending.size > 0 && this.loopGen === gen) {
            this.abort = new AbortController();
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
                const received = await this.consume(res.body);
                if (received === 0) {
                    // Accepted then closed without a single envelope (a server
                    // mid-shutdown, a proxy dropping idle connections): back
                    // off like a failure instead of reconnecting in a burst.
                    throw new Error('downlink closed without data');
                }
                // A productive connection ended (proxy timeout, worker
                // recycle): reconnect right away with a fresh backoff.
                unreachableSince = null;
                delay = this.reconnectDelay;
            } catch (err) {
                if (this.pending.size === 0 || this.loopGen !== gen) {
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
            }
        }
        if (this.loopGen === gen) {
            this.downlinkOpen = false;
            this.abort = null;
        }
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

let singleton: StreamClient | null = null;

export function getStreamClient(): StreamClient {
    if (!singleton) {
        singleton = new StreamClient();
    }
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
