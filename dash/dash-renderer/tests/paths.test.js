import {expect} from 'chai';
import {describe, it} from 'mocha';
import {appendPaths, computePaths, getPath} from '../src/actions/paths';

/*
 * Tests for the O(appended) `appendPaths` fast-path used when a Patch only
 * tail-appends children (see patchAnalysis `tailAppends`). The core guarantee
 * we assert: `appendPaths` produces the SAME id->path table that a full
 * `computePaths` recrawl would, while only visiting the newly appended items.
 * If these ever diverge, the perf fast-path is unsafe and must not be taken.
 */

const component = (id, props = {}) => ({
    namespace: 'dash_html_components',
    type: 'Div',
    props: {id, ...props}
});

// Build the children-array layout the way the store sees it: an object whose
// `props.children` is the list. Paths are computed for the whole subtree.
const container = children => component('container', {children});

// The path to the children list inside the container, rooted for the store.
const CHILDREN_PATH = ['props', 'children'];

const fullPaths = children =>
    computePaths(container(children), [], {strs: {}, objs: {}}, {});

describe('appendPaths — O(appended) path table update', () => {
    it('matches computePaths for a pure string-id tail append', () => {
        const before = [component('a'), component('b'), component('c')];
        const added = [component('d'), component('e')];
        const after = [...before, ...added];

        // full recompute (the slow, always-correct reference)
        const reference = fullPaths(after);

        // incremental: start from the pre-append table, append only new items
        const start = fullPaths(before);
        const incremental = appendPaths(
            added,
            CHILDREN_PATH,
            before.length,
            start
        );

        expect(incremental.strs).to.deep.equal(reference.strs);
        expect(incremental.objs).to.deep.equal(reference.objs);
    });

    it('keeps pre-existing entries intact and adds the new ones', () => {
        const before = [component('a'), component('b')];
        const start = fullPaths(before);
        const result = appendPaths(
            [component('c')],
            CHILDREN_PATH,
            before.length,
            start
        );
        // old ones unchanged
        expect(getPath(result, 'a')).to.deep.equal(getPath(start, 'a'));
        expect(getPath(result, 'b')).to.deep.equal(getPath(start, 'b'));
        // new one reachable at the right index
        expect(getPath(result, 'c')).to.deep.equal(['props', 'children', 2]);
    });

    it('computes paths for nested children of appended items', () => {
        const before = [component('a')];
        const added = [component('parent', {children: [component('child')]})];
        const reference = fullPaths([...before, ...added]);
        const incremental = appendPaths(
            added,
            CHILDREN_PATH,
            before.length,
            fullPaths(before)
        );
        expect(incremental.strs).to.deep.equal(reference.strs);
        // the nested child resolves under its appended parent
        expect(getPath(incremental, 'child')).to.deep.equal(
            getPath(reference, 'child')
        );
    });

    it('matches computePaths for pattern-matching (dict) ids', () => {
        const before = [
            component({type: 'item', index: 0}),
            component({type: 'item', index: 1})
        ];
        const added = [
            component({type: 'item', index: 2}),
            component({type: 'item', index: 3})
        ];
        const reference = fullPaths([...before, ...added]);
        const incremental = appendPaths(
            added,
            CHILDREN_PATH,
            before.length,
            fullPaths(before)
        );
        // objs table (dict ids) must match exactly, including ordering by index
        expect(incremental.objs).to.deep.equal(reference.objs);
        expect(incremental.strs).to.deep.equal(reference.strs);
    });

    it('handles items without ids (they contribute no path entries)', () => {
        const before = [component('a')];
        const added = [
            {namespace: 'dash_html_components', type: 'Br', props: {}},
            component('b')
        ];
        const reference = fullPaths([...before, ...added]);
        const incremental = appendPaths(
            added,
            CHILDREN_PATH,
            before.length,
            fullPaths(before)
        );
        expect(incremental.strs).to.deep.equal(reference.strs);
        expect(getPath(incremental, 'b')).to.deep.equal([
            'props',
            'children',
            2
        ]);
    });

    it('matches computePaths for an append into a nested list', () => {
        // Mirrors a nested `p[0]['props']['children'].extend(...)`: the grown
        // list lives at container.children[0].props.children, so executedCallbacks
        // roots appendPaths at CHILDREN_PATH + [0, 'props', 'children'].
        const nestedList = kids => [component('inner', {children: kids})];
        const before = nestedList([component('a'), component('b')]);
        const added = [component('c'), component('d')];
        const after = nestedList([component('a'), component('b'), ...added]);

        const reference = fullPaths(after);

        const nestedPath = [...CHILDREN_PATH, 0, 'props', 'children'];
        const incremental = appendPaths(
            added,
            nestedPath,
            2, // two pre-existing items in the nested list
            fullPaths(before)
        );

        expect(incremental.strs).to.deep.equal(reference.strs);
        expect(incremental.objs).to.deep.equal(reference.objs);
        expect(getPath(incremental, 'c')).to.deep.equal([
            'props',
            'children',
            0,
            'props',
            'children',
            2
        ]);
        // pre-existing nested entries stay put
        expect(getPath(incremental, 'a')).to.deep.equal(
            getPath(reference, 'a')
        );
        expect(getPath(incremental, 'inner')).to.deep.equal(
            getPath(reference, 'inner')
        );
    });

    it('preserves the events emitter from the old paths', () => {
        const start = fullPaths([component('a')]);
        const events = {emit: () => undefined};
        const result = appendPaths([component('b')], CHILDREN_PATH, 1, {
            ...start,
            events
        });
        expect(result.events).to.equal(events);
    });
});
