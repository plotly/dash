import isAppReady from "../src/actions/isAppReady";

const WAIT = 1000;

describe('isAppReady', () => {
    let resolve;
    beforeEach(() => {
        const promise = new Promise(r => {
            resolve = r;
        });

        window.__components = {
            a: { _dashprivate_isLazyComponentReady: promise },
            b: {}
        };
    });

    it('executes if app is ready', async () => {
        let done = false;
        Promise.resolve(isAppReady(
            [{ namespace: '__components', type: 'b', props: { id: 'comp1' } }],
            { strs: { comp1: [0] }, objs: {} },
            ['comp1']
        )).then(() => {
            done = true
        });

        await new Promise(r => setTimeout(r, WAIT));
        expect(done).toEqual(true);
    });

    it('waits on app to be ready', async () => {
        let done = false;
        Promise.resolve(isAppReady(
            [{ namespace: '__components', type: 'a', props: { id: 'comp1' } }],
            { strs: { comp1: [0] }, objs: {} },
            ['comp1']
        )).then(() => {
            done = true
        });

        await new Promise(r => setTimeout(r, WAIT));
        expect(done).toEqual(false);

        resolve();

        await new Promise(r => setTimeout(r, WAIT));
        expect(done).toEqual(true);
    });
});
