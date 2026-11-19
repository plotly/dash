import {expect} from 'chai';
import {describe, it} from 'mocha';
import {createReducer} from '../src/reducers/reducer';

const hashes = {
    'a,children,1': {hash: 1},
    'a,children,1,props,children': {hash: 1},
    'a,children,10': {hash: 1}
};

const reset = itempath => ({
    type: 'RESET_COMPONENT_STATE',
    payload: {itempath}
});

describe('RESET_COMPONENT_STATE', () => {
    const reducer = createReducer();
    const state = reducer({layoutHashes: hashes}, {type: '@@INIT'});

    it('clears the path and its descendants but not siblings', () => {
        const next = reducer(state, reset(['a', 'children', 1]));
        expect(Object.keys(next.layoutHashes)).to.deep.equal(['a,children,10']);
    });

    it('keeps the same object when nothing matches', () => {
        const next = reducer(state, reset(['b']));
        expect(next.layoutHashes).to.equal(state.layoutHashes);
    });
});
