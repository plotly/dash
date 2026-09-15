/**
 * Doubles for the multiplexed streaming transport tests: a controllable NDJSON
 * downlink body and a fetch that separates uplink, downlink and cancel POSTs.
 */

// A controllable downlink body: push NDJSON lines and close it on demand.
export function makeDownlink() {
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

// A fetch double that separates uplink POSTs from downlink and cancel POSTs.
export function makeFetch() {
    const uplinks = [];
    const downlinks = [];
    const cancels = [];
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
        if (body.streamCancel) {
            cancels.push(body.streamCancel);
            return Promise.resolve(
                new Response(
                    JSON.stringify({
                        multi: true,
                        stream: true,
                        cancelled: true
                    }),
                    {status: 200}
                )
            );
        }
        uplinks.push(body);
        return Promise.resolve(
            new Response(JSON.stringify({multi: true, stream: true}), {
                status: 200
            })
        );
    };
    return {fetchImpl, uplinks, downlinks, cancels};
}

export const tick = (ms = 5) => new Promise(r => setTimeout(r, ms));

export async function waitFor(pred, timeout = 1000) {
    const end = Date.now() + timeout;
    while (Date.now() < end) {
        if (pred()) return;
        await tick(5);
    }
    throw new Error('condition not met in time');
}

// A fetch double for POLL mode: each downlink POST returns a complete body
// holding the envelopes queued for that poll (from `queue`, a list of lists;
// empty when exhausted) and records when it was polled.
export function makePollFetch(queue = []) {
    const uplinks = [];
    const polls = [];
    const cancels = [];
    const fetchImpl = (url, init) => {
        const body = JSON.parse(init.body);
        if (body.streamDownlink) {
            const envelopes = queue.length ? queue.shift() : [];
            polls.push({
                at: Date.now(),
                from: body.streamDownlink.from,
                n: envelopes.length
            });
            const text = envelopes.map(e => JSON.stringify(e) + '\n').join('');
            return Promise.resolve(new Response(text, {status: 200}));
        }
        if (body.streamCancel) {
            cancels.push(body.streamCancel);
            return Promise.resolve(new Response('{}', {status: 200}));
        }
        uplinks.push(body);
        return Promise.resolve(
            new Response(JSON.stringify({multi: true, stream: true}), {
                status: 200
            })
        );
    };
    return {fetchImpl, uplinks, polls, cancels, queue};
}
