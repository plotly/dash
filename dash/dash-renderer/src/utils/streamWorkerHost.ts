/**
 * The worker's end of the SharedWorker streaming transport.
 *
 * One `StreamClient` (one connection id, one downlink) serves every tab of the
 * browser. Each tab connects a port and asks for streams; the host runs them on
 * the shared client and relays frames back to the asking port. When a tab
 * announces it is going away, its streams are cancelled -- dropped here and
 * cancelled server-side -- while the downlink stays up for the other tabs.
 *
 * Kept separate from the worker entry so it can be exercised with plain
 * MessageChannel ports in the unit tests.
 */

import {
    StreamClient,
    StreamHostMessage,
    StreamPort,
    StreamPortMessage
} from './streamClient';

/** The slice of SharedWorkerGlobalScope the host uses (fakeable in tests). */
export interface StreamWorkerScope {
    onconnect: ((event: MessageEvent) => void) | null;
}

interface LiveStream {
    rendererId: string;
    workerRequestId: string;
    url: string;
    init: RequestInit;
}

export function attachStreamWorkerHost(
    scope: StreamWorkerScope,
    client: StreamClient
): void {
    // Keyed by the page's request id (unique: it embeds the tab's renderer id).
    const live = new Map<string, LiveStream>();

    const post = (port: StreamPort, message: StreamPortMessage) =>
        port.postMessage(message);

    const startStream = (
        port: StreamPort,
        message: Extract<StreamHostMessage, {type: 'stream'}>
    ) => {
        const {rendererId, requestId, url, init, endId, payload, transport} =
            message;
        if (transport) {
            client.configure(transport);
        }
        const {requestId: workerRequestId, settled} = client.start(
            url,
            init,
            endId,
            payload,
            frame => post(port, {type: 'frame', requestId, frame})
        );
        live.set(requestId, {rendererId, workerRequestId, url, init});
        settled.then(
            () => {
                live.delete(requestId);
                post(port, {type: 'done', requestId});
            },
            (err: Error) => {
                // A stream cancelled on unregister was already forgotten; its
                // tab is gone and nobody is listening for the rejection.
                if (live.delete(requestId)) {
                    post(port, {
                        type: 'error',
                        requestId,
                        message: err?.message || String(err)
                    });
                }
            }
        );
    };

    const unregister = (rendererId: string) => {
        for (const [requestId, stream] of Array.from(live.entries())) {
            if (stream.rendererId === rendererId) {
                live.delete(requestId);
                client.cancel(stream.workerRequestId, stream.url, stream.init);
            }
        }
    };

    scope.onconnect = event => {
        const port = event.ports[0] as StreamPort;
        port.onmessage = e => {
            const message = e.data as StreamHostMessage;
            if (message.type === 'stream') {
                startStream(port, message);
            } else if (message.type === 'unregister') {
                unregister(message.rendererId);
            }
        };
        port.start?.();
    };
}
