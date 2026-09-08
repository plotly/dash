import {isWebSocketAvailable, isWebSocketEnabled} from '../utils/workerClient';

import type {DashConfig} from '../config';
import type {ICallback} from '../types/callbacks';

// Cap on how many callbacks may have an in-flight HTTP request to the server at
// once. This is NOT a limit on total callbacks -- it only throttles the fan-out
// of concurrent HTTP requests so the browser's ~6-connections-per-host ceiling
// doesn't stall the app under a wide callback graph. Callbacks that don't hold
// an HTTP connection for their lifetime are exempt (see `usesRequestSlot`):
// clientside callbacks (run in-browser), streaming callbacks (long-lived), and
// anything routed over the multiplexed WebSocket transport.
export const MAX_CONCURRENT_HTTP_CALLBACKS = 12;

// A callback rides the multiplexed WebSocket transport (rather than its own HTTP
// request) when websocket callbacks are enabled globally, or when it opts in
// per-callback and the transport is available. Never for background callbacks,
// which always poll over HTTP. Mirrors the routing decision in handleServerside.
export const routedOverWebSocket = (
    cb: ICallback,
    config: DashConfig
): boolean =>
    !cb.callback.background &&
    (isWebSocketEnabled(config) ||
        (Boolean(cb.callback.websocket) && isWebSocketAvailable(config)));

// True only for callbacks that hold an HTTP connection for their lifetime -- the
// only ones that count against MAX_CONCURRENT_HTTP_CALLBACKS. Clientside
// callbacks make no request, streaming callbacks are long-lived (they must not
// pin a slot for their whole life -- that would starve everything else,
// including clientside callbacks), and websocket-routed callbacks share one
// socket, so none of those count.
export const usesRequestSlot = (cb: ICallback, config: DashConfig): boolean =>
    !cb.callback.clientside_function &&
    !cb.callback.stream &&
    !routedOverWebSocket(cb, config);
