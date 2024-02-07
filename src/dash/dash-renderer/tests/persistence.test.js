import {expect} from 'chai';
import {afterEach, beforeEach, describe, it} from 'mocha';
import {recordUiEdit, stores, storePrefix} from '../src/persistence';
const longString = pow => {
    let s = 's';
    for (let i = 0; i < pow; i++) {
        s += s;
    }
    return s;
};

const fillStorage = (store, key) => {
    // double the attempted string until we fail
    // then a binary search to find the exact point of failure
    const maxPow = 30;
    let pow = 0;
    for (; pow < maxPow; pow++) {
        try {
            store.setItem(key, longString(pow));
        } catch (e) {
            break;
        }
    }
    pow--;
    let s = longString(pow);
    for (pow--; pow >= 0; pow--) {
        const s2 = s + longString(pow);
        try {
            store.setItem(key, s2);
            s = s2;
        } catch (e) {
            // s remains as is, next time we'll add half as much
        }
    }
    // finally a sanity check that nothing more can be added
    try {
        store.setItem(key + '+', 'a');
    } catch (e) {
        return;
    }
    throw new Error('Something still fits in the store?');
};

const clearStores = () => {
    window.localStorage.clear();
    window.sessionStorage.clear();
    stores.memory.clear();
    // clear all record of having tested the stores
    delete stores.local;
    delete stores.session;
};

const layoutA = storeType => ({
    namespace: 'my_components',
    type: 'C',
    props: {
        id: 'a',
        persistence: true,
        persistence_type: storeType
    }
});

describe('storage fallbacks and equivalence', () => {
    const propVal = 42;
    const propStr = String(propVal);
    let dispatchCalls;

    const _dispatch = evt => {
        // verify that dispatch is sending errors to the devtools,
        // and record the message sent
        expect(evt.type).to.equal('ON_ERROR');
        dispatchCalls.push(evt.payload.error.message);
    };

    beforeEach(() => {
        window.my_components = {
            C: {
                defaultProps: {
                    persistence_type: 'local',
                    persisted_props: ['p1', 'p2']
                }
            }
        };

        dispatchCalls = [];

        clearStores();
    });

    afterEach(() => {
        delete window.my_components;
        clearStores();
    });

    ['local', 'session'].forEach(storeType => {
        const storeName = storeType + 'Storage';
        const store = window[storeName];

        const layout = layoutA(storeType);

        it(`empty ${storeName} works`, () => {
            recordUiEdit(layout, {p1: propVal}, _dispatch);
            expect(dispatchCalls).to.deep.equal([]);
            expect(store.getItem(`${storePrefix}a.p1.true`)).to.equal(
                `[${propStr}]`
            );
        });

        it(`${storeName} full from persistence works with warnings`, () => {
            fillStorage(store, `${storePrefix}x.x`);

            recordUiEdit(layout, {p1: propVal}, _dispatch);
            expect(dispatchCalls).to.deep.equal([
                `${storeName} init first try failed; clearing and retrying`,
                `${storeName} init set/get succeeded after clearing!`
            ]);
            expect(store.getItem(`${storePrefix}a.p1.true`)).to.equal(
                `[${propStr}]`
            );
            // Boolean so we don't see the very long value if test fails
            const x = Boolean(store.getItem(`${storePrefix}x.x`));
            expect(x).to.equal(false);
        });

        it(`${storeName} full from other stuff falls back on memory`, () => {
            fillStorage(store, 'not_ours');

            recordUiEdit(layout, {p1: propVal}, _dispatch);
            expect(dispatchCalls).to.deep.deep.equal([
                `${storeName} init first try failed; clearing and retrying`,
                `${storeName} init still failed, falling back to memory`
            ]);
            expect(stores.memory.getItem('a.p1.true')).to.deep.equal([propVal]);
            const x = Boolean(store.getItem('not_ours'));
            expect(x).to.equal(true);
        });

        it(`${storeName} that fills up later on just logs an error`, () => {
            // Maybe not ideal long-term behavior, but this is what happens

            // initialize and ensure the store is happy
            recordUiEdit(layout, {p1: propVal}, _dispatch);
            expect(dispatchCalls).to.deep.deep.equal([]);

            // now flood it.
            recordUiEdit(layout, {p1: longString(26)}, _dispatch);
            expect(dispatchCalls).to.deep.equal([
                `a.p1.true failed to save in ${storeName}. Persisted props may be lost.`
            ]);
        });
    });

    ['local', 'session', 'memory'].forEach(storeType => {
        const layout = layoutA(storeType);
        const key = 'key';

        it(`${storeType} primitives in/out match`, () => {
            // ensure storage is instantiated
            recordUiEdit(layout, {p1: propVal}, _dispatch);
            const store = stores[storeType];
            [
                0,
                1,
                1.1,
                true,
                false,
                null,
                undefined,
                '',
                'hi',
                '0',
                '1'
            ].forEach(val => {
                store.setItem(key, val);
                expect(store.getItem(key)).to.equal(val);
            });
        });

        it(`${storeType} arrays and objects in/out are clones`, () => {
            recordUiEdit(layout, {p1: propVal}, _dispatch);
            const store = stores[storeType];

            [[1, 2, 3], {a: 1, b: 2}].forEach(val => {
                store.setItem(key, val);
                const valOut = store.getItem(key);
                expect(valOut).not.to.equal(val);
                expect(valOut).to.deep.equal(val);
            });
        });
    });
});
