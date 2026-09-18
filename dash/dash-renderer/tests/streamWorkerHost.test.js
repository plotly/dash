import {expect} from 'chai';
import {beforeEach, describe, it} from 'mocha';

import {SharedStreamClient, StreamClient} from '../src/utils/streamClient';
import {attachStreamWorkerHost} from '../src/utils/streamWorkerHost';
import {makeFetch, waitFor} from './helpers/streamMocks';

// The worker side: one StreamClient (one downlink) behind a fake worker scope.
// Each "tab" is a MessageChannel: port1 connects to the host, port2 is the
// page's SharedStreamClient.
function makeWorker() {
    const mock = makeFetch();
    const client = new StreamClient({
        fetchImpl: mock.fetchImpl,
        reconnectDelay: 10
    });
    const scope = {onconnect: null};
    attachStreamWorkerHost(scope, client);
    const connectTab = rendererId => {
        const channel = new MessageChannel();
        scope.onconnect({ports: [channel.port1]});
        return new SharedStreamClient(channel.port2, rendererId);
    };
    return {mock, client, connectTab};
}

describe('SharedWorker stream transport', () => {
    let worker;
    beforeEach(() => {
        worker = makeWorker();
    });

    it('relays frames and the terminal done back to the asking tab', async () => {
        const tab = worker.connectTab('tab-a');
        const frames = [];
        const settled = tab.run('/cb', {}, 'e1', {output: 'a.b'}, f =>
            frames.push(f)
        );
        await waitFor(() => worker.mock.downlinks.length === 1);
        // The uplink carried the tab's signed endId and the payload.
        const conn = worker.mock.uplinks[0].streamConnection;
        expect(worker.mock.uplinks[0].url).to.equal('/cb?endId=e1');
        expect(worker.client.connectionEndId).to.equal('e1');
        expect(worker.mock.uplinks[0].output).to.equal('a.b');

        const dl = worker.mock.downlinks[0].dl;
        dl.push({rid: conn.requestId, frame: {response: {a: 1}}, seq: 1});
        dl.push({rid: conn.requestId, frame: {done: true}, seq: 2});
        await settled;
        expect(frames).to.deep.equal([{response: {a: 1}}]);
        expect(tab.activeCount).to.equal(0);
    });

    it('rejects the tab on an error frame', async () => {
        const tab = worker.connectTab('tab-a');
        const settled = tab.run('/cb', {}, 'e1', {output: 'a'}, () => {});
        await waitFor(() => worker.mock.downlinks.length === 1);
        const {requestId} = worker.mock.uplinks[0].streamConnection;
        worker.mock.downlinks[0].dl.push({
            rid: requestId,
            frame: {done: true, error: {message: 'boom'}},
            seq: 1
        });
        let err;
        await settled.catch(e => (err = e));
        expect(err.message).to.contain('boom');
    });

    it('serves several tabs over one downlink, routed to the right tab', async () => {
        const tabA = worker.connectTab('tab-a');
        const tabB = worker.connectTab('tab-b');
        const aFrames = [];
        const bFrames = [];
        const a = tabA.run('/cb', {}, 'e1', {output: 'a'}, f =>
            aFrames.push(f)
        );
        const b = tabB.run('/cb', {}, 'e2', {output: 'b'}, f =>
            bFrames.push(f)
        );
        await waitFor(() => worker.mock.uplinks.length === 2);
        expect(worker.mock.downlinks.length).to.equal(1);
        // Tab B's stream rides tab A's connection: one endId keys the topic.
        expect(worker.mock.uplinks[1].url).to.equal('/cb?endId=e1');
        const ridA = worker.mock.uplinks[0].streamConnection.requestId;
        const ridB = worker.mock.uplinks[1].streamConnection.requestId;
        const dl = worker.mock.downlinks[0].dl;
        dl.push({rid: ridB, frame: {response: {b: 1}}, seq: 1});
        dl.push({rid: ridA, frame: {response: {a: 1}}, seq: 2});
        dl.push({rid: ridA, frame: {done: true}, seq: 3});
        dl.push({rid: ridB, frame: {done: true}, seq: 4});
        await Promise.all([a, b]);
        expect(aFrames).to.deep.equal([{response: {a: 1}}]);
        expect(bFrames).to.deep.equal([{response: {b: 1}}]);
    });

    it('cancels a departing tab’s streams server-side and keeps serving the rest', async () => {
        const tabA = worker.connectTab('tab-a');
        const tabB = worker.connectTab('tab-b');
        const bFrames = [];
        const a = tabA.run('/cb', {}, 'e1', {output: 'a'}, () => {});
        const b = tabB.run('/cb', {}, 'e2', {output: 'b'}, f =>
            bFrames.push(f)
        );
        await waitFor(() => worker.mock.uplinks.length === 2);
        const ridA = worker.mock.uplinks[0].streamConnection.requestId;
        const ridB = worker.mock.uplinks[1].streamConnection.requestId;

        tabA.release(); // tab A closed
        await waitFor(() => worker.mock.cancels.length === 1);
        expect(worker.mock.cancels[0]).to.deep.equal({
            url: '/cb?endId=e1',
            requestId: ridA
        });
        // Tab B still has a stream in flight: the shared downlink stays open.
        expect(worker.mock.downlinks[0].signal.aborted).to.equal(false);

        const dl = worker.mock.downlinks[0].dl;
        dl.push({rid: ridA, frame: {response: {a: 1}}, seq: 1}); // dropped
        dl.push({rid: ridB, frame: {response: {b: 1}}, seq: 2});
        dl.push({rid: ridB, frame: {done: true}, seq: 3});
        await b;
        expect(bFrames).to.deep.equal([{response: {b: 1}}]);
        // Nobody is left listening for A; its page-side promise stays pending
        // (the tab is gone) rather than surfacing an error anywhere.
        expect(tabA.activeCount).to.equal(1);
        void a;
        // With B done and A cancelled, the downlink is released.
        expect(worker.mock.downlinks[0].signal.aborted).to.equal(true);
    });

    it('fail() rejects everything in flight and marks the transport broken', async () => {
        const tab = worker.connectTab('tab-a');
        const settled = tab.run('/cb', {}, 'e1', {output: 'a'}, () => {});
        tab.fail(new Error('worker died'));
        let err;
        await settled.catch(e => (err = e));
        expect(err.message).to.equal('worker died');
        expect(tab.broken).to.equal(true);
    });

    it('adopts the downlink mode the page passes along', async () => {
        const channel = new MessageChannel();
        const scope = {onconnect: null};
        attachStreamWorkerHost(scope, worker.client);
        scope.onconnect({ports: [channel.port1]});
        const tab = new SharedStreamClient(channel.port2, 'tab-a', {
            mode: 'poll',
            pollInterval: 250
        });
        tab.run('/cb', {}, 'e1', {output: 'a'}, () => {});
        await waitFor(() => worker.mock.uplinks.length === 1);
        expect(worker.client.transport).to.deep.equal({
            mode: 'poll',
            pollInterval: 250
        });
    });
});
