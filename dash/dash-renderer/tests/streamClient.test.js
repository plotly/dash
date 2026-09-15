import {expect} from 'chai';
import {beforeEach, describe, it} from 'mocha';

import {StreamClient} from '../src/utils/streamClient';
import {makeFetch, makePollFetch, tick, waitFor} from './helpers/streamMocks';

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

    it('cancel drops the request, tells the server, and closes an idle downlink', async () => {
        const frames = [];
        const {requestId, settled} = client.start('/cb', {}, {output: 'a'}, f =>
            frames.push(f)
        );
        await waitFor(() => mock.downlinks.length === 1);
        expect(mock.uplinks[0].streamConnection.requestId).to.equal(requestId);

        client.cancel(requestId, '/cb', {});
        let err;
        await settled.catch(e => (err = e));
        expect(err.message).to.contain('cancelled');
        expect(mock.cancels).to.deep.equal([
            {connectionId: client.connectionId, requestId}
        ]);
        // No consumer remains, so the downlink is released.
        expect(mock.downlinks[0].signal.aborted).to.equal(true);
        // A late frame for the cancelled request is dropped, not delivered.
        client.dispatchEnvelope({
            rid: requestId,
            frame: {response: {a: 1}},
            seq: 1
        });
        expect(frames).to.deep.equal([]);
    });
});

describe('StreamClient in poll mode', () => {
    // A frame for whatever request id the first uplink carried.
    const frameFor = rid => ({rid, frame: {response: {a: 1}}, seq: 1});
    const doneFor = rid => ({rid, frame: {done: true}, seq: 2});

    it('re-polls promptly while frames flow and resolves on done', async () => {
        const mock = makePollFetch();
        const client = new StreamClient({
            fetchImpl: mock.fetchImpl,
            mode: 'poll',
            pollInterval: 20
        });
        const frames = [];
        const settled = client.run('/cb', {}, {output: 'a'}, f =>
            frames.push(f)
        );
        await waitFor(() => mock.uplinks.length === 1);
        const rid = mock.uplinks[0].streamConnection.requestId;
        mock.queue.push([frameFor(rid)], [doneFor(rid)]);
        await settled;
        expect(frames).to.deep.equal([{response: {a: 1}}]);
        // The second poll resumed from the first frame's sequence.
        const withFrames = mock.polls.filter(p => p.n > 0);
        expect(withFrames.length).to.equal(2);
        expect(mock.polls[mock.polls.length - 1].from).to.equal(1);
        // Every response ended at once: nothing is left holding a connection.
        expect(client.activeCount).to.equal(0);
    });

    it('backs off while quiet, bounded, and polls at once for a new stream', async () => {
        const mock = makePollFetch();
        const client = new StreamClient({
            fetchImpl: mock.fetchImpl,
            mode: 'poll',
            pollInterval: 30
        });
        client.run('/cb', {}, {output: 'a'}, () => {});
        await waitFor(() => mock.uplinks.length === 1);
        // Idle polls hold the 30ms pace for two polls, then back off
        // geometrically (60, 120, 240, 300 capped at 10x).
        await waitFor(() => mock.polls.length >= 6, 4000);
        const gaps = mock.polls.slice(1).map((p, i) => p.at - mock.polls[i].at);
        expect(Math.max(gaps[0], gaps[1])).to.be.lessThan(90);
        expect(gaps[3]).to.be.greaterThan(gaps[2] * 1.3);
        expect(gaps[4]).to.be.greaterThan(gaps[3] * 1.3);
        // A new stream wakes the pause: the next poll comes right away.
        const before = mock.polls.length;
        client.run('/cb', {}, {output: 'b'}, () => {});
        await tick(15);
        expect(mock.polls.length).to.be.greaterThan(before);
    });

    it('in stream mode, an empty clean end waits the reconnect delay (no hot loop)', async () => {
        const mock = makePollFetch();
        const client = new StreamClient({
            fetchImpl: mock.fetchImpl,
            reconnectDelay: 30
        });
        client.run('/cb', {}, {output: 'a'}, () => {});
        await waitFor(() => mock.polls.length >= 4, 2000);
        const span = mock.polls[3].at - mock.polls[0].at;
        expect(span).to.be.at.least(80);
        expect(span).to.be.lessThan(600);
        expect(client.transport.mode).to.equal(undefined);
    });
});
