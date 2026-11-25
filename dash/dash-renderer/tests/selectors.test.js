import {expect} from 'chai';
import {before, describe, it} from 'mocha';
import {selectDashProps} from '../src/wrapper/selectors';

const leaf = {namespace: 'test_ns', type: 'Leaf', props: {}};
const flagged = children => ({
    namespace: 'test_ns',
    type: 'Listens',
    props: {children}
});

// The selector remembers the hashes it has seen in a module-level record, so
// each test uses its own child index to stay independent of the others.
const stateFor = (index, layoutHashes) => {
    const children = [];
    children[index] = flagged([leaf]);
    return {layout: {props: {children}}, layoutHashes};
};

const select = (index, layoutHashes) => {
    const path = ['props', 'children', index];
    const [, , hash, changedProps, renderType] = selectDashProps(path)(
        stateFor(index, layoutHashes)
    );
    return {hash, changedProps, renderType};
};

describe('selectDashProps with dashChildrenUpdate', () => {
    before(() => {
        window.test_ns = {Listens: {dashChildrenUpdate: true}, Leaf: {}};
    });

    it('sums its own hash and those of its first level children', () => {
        const self = 'props,children,1';
        const {hash} = select(1, {
            [self]: {hash: 1},
            [`${self},props,children`]: {hash: 10},
            [`${self},props,children,0`]: {hash: 100}
        });
        expect(hash).to.equal(111);
    });

    it('ignores deeper descendants and unrelated paths', () => {
        const self = 'props,children,2';
        const {hash} = select(2, {
            [self]: {hash: 1},
            [`${self},props,children,0,props,children`]: {hash: 10},
            'props,children,3': {hash: 100},
            props: {hash: 1000}
        });
        expect(hash).to.equal(1);
    });

    it('does not mistake a sibling with the same prefix for a child', () => {
        const self = 'props,children,4';
        const {hash, changedProps} = select(4, {
            [self]: {hash: 1},
            'props,children,40': {hash: 10},
            'props,children,40,props,children': {hash: 100}
        });
        expect(hash).to.equal(1);
        expect(changedProps).to.deep.equal({});
    });

    it('reports the prop of an updated child only once', () => {
        const hashes = {'props,children,5,props,children': {hash: 1}};
        expect(select(5, hashes)).to.deep.equal({
            hash: 1,
            changedProps: {children: true},
            renderType: 'components'
        });
        expect(select(5, hashes)).to.deep.equal({
            hash: 1,
            changedProps: {},
            renderType: undefined
        });
    });

    it('reports its own changed props and render type', () => {
        const {hash, changedProps, renderType} = select(6, {
            'props,children,6': {
                hash: 2,
                changedProps: {value: 1},
                renderType: 'callback'
            }
        });
        expect(hash).to.equal(2);
        expect(changedProps).to.deep.equal({value: 1});
        expect(renderType).to.equal('callback');
    });
});
