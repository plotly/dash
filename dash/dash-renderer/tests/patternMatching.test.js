import {expect} from 'chai';
import {beforeEach, describe, it} from 'mocha';
import {getAllPMCIds, replacePMC} from '../src/actions/patternMatching';

// Minimal stand-in for the pieces of the redux state that the pattern
// matching helpers read.
function makeState(objs) {
    return {paths: {strs: {}, objs: objs || {}}};
}

// A wildcard entry as produced by crawling the layout: `values` is the list
// of id values ordered by the (sorted) id keys.
function entries(keyStr, valueLists) {
    return {
        [keyStr]: valueLists.map((values, i) => ({
            values,
            path: ['props', 'children', i]
        }))
    };
}

const cb = {parsedChangedPropsIds: [{id: 'home1', type: 'loading'}]};

describe('getAllPMCIds', () => {
    it('returns the matching ids when the wildcard key is registered', () => {
        const state = makeState(
            entries('id,type', [
                ['home1', 'loading'],
                ['home2', 'loading']
            ])
        );
        const result = getAllPMCIds(
            {id: ['ALL'], type: 'loading'},
            state,
            'id'
        );
        expect(result).to.deep.equal([
            {id: 'home1', type: 'loading'},
            {id: 'home2', type: 'loading'}
        ]);
    });

    it('returns an empty list when no component uses that id shape', () => {
        // This is the state on a page that renders none of the wildcard
        // components: `paths.objs['id,type']` was never populated.
        const result = getAllPMCIds(
            {id: ['ALL'], type: 'loading'},
            makeState({}),
            'id'
        );
        expect(result).to.deep.equal([]);
    });
});

describe('replacePMC', () => {
    let getState;

    beforeEach(() => {
        getState = () =>
            makeState(
                entries('id,type', [
                    ['home1', 'loading'],
                    ['home2', 'loading']
                ])
            );
    });

    it('expands ALL to every matching component', () => {
        const result = replacePMC(
            {id: ['ALL'], type: 'loading'},
            cb,
            0,
            getState
        );
        expect(result).to.deep.equal([
            {id: 'home1', type: 'loading'},
            {id: 'home2', type: 'loading'}
        ]);
    });

    it('resolves MATCH against the triggering id', () => {
        const result = replacePMC(
            {id: ['MATCH'], type: 'loading'},
            cb,
            0,
            getState
        );
        expect(result).to.deep.equal([{id: 'home1', type: 'loading'}]);
    });

    it('leaves a fully concrete id untouched', () => {
        const result = replacePMC(
            {id: 'home1', type: 'loading'},
            cb,
            0,
            getState
        );
        expect(result).to.deep.equal([{id: 'home1', type: 'loading'}]);
    });

    it('yields no ids when ALL matches nothing on the current page', () => {
        // Regression test for #3297: navigating to a page that has none of
        // the wildcard components used to throw
        // `state.paths.objs[idKey] is undefined`, and later returned a
        // partial id missing the wildcard key.
        const empty = () => makeState({});
        const result = replacePMC({id: ['ALL'], type: 'loading'}, cb, 0, empty);
        expect(result).to.deep.equal([]);
    });

    it('yields no ids when ALLSMALLER matches nothing on the current page', () => {
        const empty = () => makeState({});
        const result = replacePMC(
            {id: ['ALLSMALLER'], type: 'loading'},
            cb,
            0,
            empty
        );
        expect(result).to.deep.equal([]);
    });
});
