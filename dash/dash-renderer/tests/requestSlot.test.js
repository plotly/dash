import {expect} from 'chai';
import {describe, it} from 'mocha';

import {
    MAX_CONCURRENT_HTTP_CALLBACKS,
    routedOverWebSocket,
    usesRequestSlot
} from '../src/observers/requestSlot';

// Build a minimal ICallback with only the fields the scheduler inspects.
const cb = definition => ({callback: {websocket: false, ...definition}});

// Config flavors. isWebSocketEnabled/isWebSocketAvailable also require
// SharedWorker, which exists in the (Chrome) karma runner.
const HTTP = {};
const WS_ENABLED = {websocket: {enabled: true, url: '/ws', worker_url: '/w'}};
const WS_AVAILABLE_NOT_ENABLED = {
    websocket: {enabled: false, url: '/ws', worker_url: '/w'}
};

describe('prioritizedCallbacks request-slot accounting', () => {
    it('the concurrency cap is 12', () => {
        expect(MAX_CONCURRENT_HTTP_CALLBACKS).to.equal(12);
    });

    describe('usesRequestSlot', () => {
        it('a plain serverside HTTP callback counts against the budget', () => {
            expect(usesRequestSlot(cb({}), HTTP)).to.equal(true);
        });

        it('excludes clientside callbacks (they run in-browser)', () => {
            const clientside = cb({
                clientside_function: {namespace: 'ns', function_name: 'fn'}
            });
            expect(usesRequestSlot(clientside, HTTP)).to.equal(false);
        });

        it('excludes streaming callbacks (they are long-lived)', () => {
            expect(usesRequestSlot(cb({stream: true}), HTTP)).to.equal(false);
        });

        it('excludes every non-background callback when websocket is enabled', () => {
            expect(usesRequestSlot(cb({}), WS_ENABLED)).to.equal(false);
        });

        it('still counts background callbacks even with websocket enabled', () => {
            const background = cb({background: {interval: 1000}});
            expect(usesRequestSlot(background, WS_ENABLED)).to.equal(true);
        });

        it('excludes per-callback websocket routing when the transport is available', () => {
            const perCallbackWs = cb({websocket: true});
            expect(
                usesRequestSlot(perCallbackWs, WS_AVAILABLE_NOT_ENABLED)
            ).to.equal(false);
        });

        it('counts a per-callback websocket that falls back to HTTP (transport unavailable)', () => {
            const perCallbackWs = cb({websocket: true});
            expect(usesRequestSlot(perCallbackWs, HTTP)).to.equal(true);
        });
    });

    describe('routedOverWebSocket', () => {
        it('routes non-background callbacks over the socket when enabled', () => {
            expect(routedOverWebSocket(cb({}), WS_ENABLED)).to.equal(true);
        });

        it('never routes background callbacks over the socket', () => {
            const background = cb({background: {interval: 1000}});
            expect(routedOverWebSocket(background, WS_ENABLED)).to.equal(false);
        });

        it('keeps callbacks on HTTP when no websocket transport is configured', () => {
            expect(routedOverWebSocket(cb({}), HTTP)).to.equal(false);
        });
    });
});
