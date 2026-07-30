import {expect} from 'chai';
import {beforeEach, describe, it} from 'mocha';

import {StreamClient} from '../src/utils/streamClient';

// A controllable downlink body: push NDJSON lines and close it on demand.
function makeDownlink() {
    let controller;
    const stream = new ReadableStream({
        start(c) {
            controller = c;
        }
    });
    const enc = new TextEncoder();
    return {
        stream,
        push: obj => controller.enqueue(enc.encode(JSON.stringify(obj) + '\n')),
        pushRaw: text => controller.enqueue(enc.encode(text)),
        close: () => controller.close()
    };
}

// A fetch double that separates uplink POSTs from downlink POSTs.
function makeFetch() {
    const uplinks = [];
    const downlinks = [];
    const fetchImpl = (url, init) => {
        const body = JSON.parse(init.body);
        if (body.streamDownlink) {
            const dl = makeDownlink();
            downlinks.push({
                from: body.streamDownlink.from,
                signal: init.signal,
                dl
            });
            return Promise.resolve(new Response(dl.stream, {status: 200}));
        }
        uplinks.push(body);
        return Promise.resolve(
            new Response(JSON.stringify({multi: true, stream: true}), {
                status: 200
            })
        );
    };
    return {fetchImpl, uplinks, downlinks};
}

const tick = (ms = 5) => new Promise(r => setTimeout(r, ms));
async function waitFor(pred, timeout = 1000) {
    const end = Date.now() + timeout;
    while (Date.now() < end) {
        if (pred()) return;
        await tick(5);
    }
    throw new Error('condition not met in time');
}

describe('StreamClient', () => {
    let mock;
    let client;
    beforeEach(() => {
        mock = makeFetch();
        client = new StreamClient({
            fetchImpl: mock.fetchImpl,
            reconnectDelay: 10
        });
    });

    it('sends an uplink tagging the callback with a connection + request id', async () => {
        client.run('/cb', {}, {output: 'a.b'}, () => {});
        await waitFor(() => mock.uplinks.length === 1);
        const conn = mock.uplinks[0].streamConnection;
        expect(conn.connectionId).to.be.a('string');
        expect(conn.requestId).to.be.a('string');
        expect(mock.uplinks[0].output).to.equal('a.b'); // original payload preserved
    });

    it('routes frames to onFrame and resolves on the done frame', async () => {
        const frames = [];
        const settled = client.run('/cb', {}, {output: 'a.b'}, f =>
            frames.push(f)
        );
        await waitFor(() => mock.downlinks.length === 1);
        const {requestId} = mock.uplinks[0].streamConnection;
        const dl = mock.downlinks[0].dl;

        dl.push({rid: requestId, frame: {response: {a: 1}}, seq: 1});
        dl.push({rid: requestId, frame: {response: {a: 2}}, seq: 2});
        dl.push({rid: requestId, frame: {done: true}, seq: 3});

        await settled;
        expect(frames).to.deep.equal([{response: {a: 1}}, {response: {a: 2}}]);
        // The downlink is aborted once no callbacks remain in flight.
        expect(mock.downlinks[0].signal.aborted).to.equal(true);
    });

    it('rejects on an error done frame', async () => {
        const settled = client.run('/cb', {}, {output: 'a.b'}, () => {});
        await waitFor(() => mock.downlinks.length === 1);
        const {requestId} = mock.uplinks[0].streamConnection;
        mock.downlinks[0].dl.push({
            rid: requestId,
            frame: {done: true, error: {message: 'boom'}},
            seq: 1
        });
        let err;
        await settled.catch(e => (err = e));
        expect(err).to.be.an('error');
        expect(err.message).to.contain('boom');
    });

    it('multiplexes two callbacks over one downlink, routed by request id', async () => {
        const aFrames = [];
        const bFrames = [];
        const a = client.run('/cb', {}, {output: 'a'}, f => aFrames.push(f));
        const b = client.run('/cb', {}, {output: 'b'}, f => bFrames.push(f));
        await waitFor(() => mock.uplinks.length === 2);
        // Both share a single downlink connection.
        expect(mock.downlinks.length).to.equal(1);
        const ridA = mock.uplinks[0].streamConnection.requestId;
        const ridB = mock.uplinks[1].streamConnection.requestId;
        const dl = mock.downlinks[0].dl;

        dl.push({rid: ridB, frame: {response: {b: 1}}, seq: 1});
        dl.push({rid: ridA, frame: {response: {a: 1}}, seq: 2});
        dl.push({rid: ridA, frame: {done: true}, seq: 3});
        dl.push({rid: ridB, frame: {done: true}, seq: 4});

        await Promise.all([a, b]);
        expect(aFrames).to.deep.equal([{response: {a: 1}}]);
        expect(bFrames).to.deep.equal([{response: {b: 1}}]);
    });

    it('reconnects from the last seen sequence when the downlink drops', async () => {
        const frames = [];
        const settled = client.run('/cb', {}, {output: 'a'}, f =>
            frames.push(f)
        );
        await waitFor(() => mock.downlinks.length === 1);
        const {requestId} = mock.uplinks[0].streamConnection;

        mock.downlinks[0].dl.push({
            rid: requestId,
            frame: {response: {a: 1}},
            seq: 5
        });
        await waitFor(() => frames.length === 1);
        mock.downlinks[0].dl.close(); // drop mid-stream

        // It reconnects, resuming after the last applied sequence.
        await waitFor(() => mock.downlinks.length === 2);
        expect(mock.downlinks[1].from).to.equal(5);
        mock.downlinks[1].dl.push({
            rid: requestId,
            frame: {done: true},
            seq: 6
        });
        await settled;
        expect(frames).to.deep.equal([{response: {a: 1}}]);
    });

    it('skips keepalive blank lines', async () => {
        const frames = [];
        const settled = client.run('/cb', {}, {output: 'a'}, f =>
            frames.push(f)
        );
        await waitFor(() => mock.downlinks.length === 1);
        const {requestId} = mock.uplinks[0].streamConnection;
        const dl = mock.downlinks[0].dl;
        dl.pushRaw('\n'); // keepalive
        dl.push({rid: requestId, frame: {response: {a: 1}}, seq: 1});
        dl.pushRaw('\n');
        dl.push({rid: requestId, frame: {done: true}, seq: 2});
        await settled;
        expect(frames).to.deep.equal([{response: {a: 1}}]);
    });
});
