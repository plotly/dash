import {expect} from 'chai';
import {beforeEach, describe, it} from 'mocha';
import isAppReady from '../src/actions/isAppReady';
import {EventEmitter} from '../src/actions/utils';

const WAIT = 500;

describe('isAppReady', () => {
    let resolve;
    beforeEach(() => {
        const promise = new Promise(r => {
            resolve = r;
        });

        window.__components = {
            a: {_dashprivate_isLazyComponentReady: promise},
            b: {}
        };
    });

    const emitter = new EventEmitter();

    it('executes if app is ready', async () => {
        let done = false;
        Promise.resolve(
            isAppReady(
                [{namespace: '__components', type: 'b', props: {id: 'comp1'}}],
                {strs: {comp1: [0]}, objs: {}, events: emitter},
                ['comp1']
            )
        ).then(() => {
            done = true;
        });

        await new Promise(r => setTimeout(r, WAIT));
        expect(done).to.equal(true);
    });

    it('waits on app to be ready', async () => {
        let done = false;
        Promise.resolve(
            isAppReady(
                [{namespace: '__components', type: 'a', props: {id: 'comp1'}}],
                {strs: {comp1: [0]}, objs: {}, events: emitter},
                ['comp1']
            )
        ).then(() => {
            done = true;
        });

        await new Promise(r => setTimeout(r, WAIT));
        expect(done).to.equal(false);

        resolve();

        await new Promise(r => setTimeout(r, WAIT));
        expect(done).to.equal(true);
    });
});
