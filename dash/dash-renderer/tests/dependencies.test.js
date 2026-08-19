import {expect} from 'chai';
import {beforeEach, describe, it} from 'mocha';
import {
    computeGraphs,
    getAnyVals,
    getUnfilteredLayoutCallbacks,
    getWatchedKeys
} from '../src/actions/dependencies';
import {getCallbacksByInput} from '../src/actions/dependencies_ts';
import {EventEmitter} from '../src/actions/utils';

const config = {validate_callbacks: true};

// Build a paths fixture that matches the layout crawling output
// (paths.strs for string ids, paths.objs for wildcard ids).
function makePaths(stringIds, wildcardItems) {
    const paths = {
        strs: {},
        objs: {},
        events: new EventEmitter()
    };
    stringIds.forEach(id => {
        paths.strs[id] = ['props', 'children', 0];
    });
    Object.entries(wildcardItems || {}).forEach(([keyStr, items]) => {
        paths.objs[keyStr] = items.map((values, i) => ({
            values,
            path: ['props', 'children', i]
        }));
    });
    return paths;
}

describe('dependencies — MATCH validation (#2462)', () => {
    let errors;
    const dispatchError = (message, lines) => {
        errors.push({message, lines});
    };

    beforeEach(() => {
        errors = [];
    });

    it('permits MATCH Input with fixed-id Output', () => {
        computeGraphs(
            [
                {
                    output: 'out.children',
                    inputs: [{id: '{"id":["MATCH"]}', property: 'n_clicks'}],
                    state: [],
                    no_output: false
                }
            ],
            dispatchError,
            config
        );
        expect(errors).to.eql([]);
    });

    it('permits MATCH Input with no-output callback', () => {
        computeGraphs(
            [
                {
                    output: '',
                    inputs: [{id: '{"id":["MATCH"]}', property: 'n_clicks'}],
                    state: [],
                    no_output: true
                }
            ],
            dispatchError,
            config
        );
        expect(errors).to.eql([]);
    });

    it('permits MATCH State with fixed-id Output', () => {
        computeGraphs(
            [
                {
                    output: 'out.children',
                    inputs: [{id: '{"id":["MATCH"]}', property: 'n_clicks'}],
                    state: [{id: '{"id":["MATCH"]}', property: 'id'}],
                    no_output: false
                }
            ],
            dispatchError,
            config
        );
        expect(errors).to.eql([]);
    });

    it('permits MATCH Input with ALL-only wildcard Output', () => {
        computeGraphs(
            [
                {
                    output: '{"id":["ALL"]}.children',
                    inputs: [
                        {
                            id: '{"type":"btn","idx":["MATCH"]}',
                            property: 'n_clicks'
                        }
                    ],
                    state: [],
                    no_output: false
                }
            ],
            dispatchError,
            config
        );
        expect(errors).to.eql([]);
    });

    it('still errors on ALLSMALLER Input with fixed Output', () => {
        computeGraphs(
            [
                {
                    output: 'out.children',
                    inputs: [{id: '{"id":["ALLSMALLER"]}', property: 'value'}],
                    state: [],
                    no_output: false
                }
            ],
            dispatchError,
            config
        );
        expect(errors).to.have.lengthOf(1);
        expect(errors[0].message).to.equal(
            '`Input` / `State` wildcards not in `Output`s'
        );
    });

    it('still errors when Output has MATCH on different keys than Input', () => {
        computeGraphs(
            [
                {
                    output: '{"a":["MATCH"]}.children',
                    inputs: [{id: '{"b":["MATCH"]}', property: 'n_clicks'}],
                    state: [],
                    no_output: false
                }
            ],
            dispatchError,
            config
        );
        // Should produce an error because out has MATCH on "a"
        // but input has MATCH on "b".
        expect(errors).to.have.lengthOf(1);
        expect(errors[0].message).to.equal(
            '`Input` / `State` wildcards not in `Output`s'
        );
    });

    it('still errors on Mismatched MATCH across Outputs', () => {
        computeGraphs(
            [
                {
                    output: '..{"b":["MATCH"]}.children...{"b":["ALL"],"c":1}.children..',
                    inputs: [
                        {id: '{"b":["MATCH"],"c":2}', property: 'children'}
                    ],
                    state: [],
                    no_output: false
                }
            ],
            dispatchError,
            config
        );
        const msgs = errors.map(e => e.message);
        expect(msgs).to.include(
            'Mismatched `MATCH` wildcards across `Output`s'
        );
    });
});

describe('dependencies — partial pattern indexes', () => {
    const dispatchError = () => {};

    it('keeps partial indexes empty and skips property filtering when unused', () => {
        const graphs = computeGraphs(
            [
                {
                    output: 'out.children',
                    inputs: [
                        {
                            id: '{"index":["ALL"],"type":"btn"}',
                            property: 'n_clicks'
                        }
                    ],
                    state: [],
                    no_output: false
                }
            ],
            dispatchError,
            config
        );
        let filterCalled = false;
        const newProps = {
            length: 1,
            filter: () => {
                filterCalled = true;
                return [];
            }
        };

        expect(graphs.hasPartialPatterns).to.equal(false);
        expect(graphs.partialInputPatterns).to.eql({});
        expect(graphs.partialOutputPatterns).to.eql({});
        expect(
            getWatchedKeys(
                {index: 1, page: 'home', type: 'btn'},
                newProps,
                graphs
            )
        ).to.eql([]);
        expect(filterCalled).to.equal(false);
    });

    it('indexes only partial input and output patterns', () => {
        const graphs = computeGraphs(
            [
                {
                    output: 'input-result.children',
                    inputs: [
                        {
                            id: '{"type":"btn"}',
                            property: 'n_clicks',
                            partial: true
                        },
                        {
                            id: '{"index":["ALL"],"type":"btn"}',
                            property: 'n_clicks'
                        }
                    ],
                    state: [],
                    no_output: false
                },
                {
                    output: '{"type":"display"}.children',
                    outputs_meta: [{partial: true}],
                    inputs: [{id: 'trigger', property: 'n_clicks'}],
                    state: [],
                    no_output: false
                }
            ],
            dispatchError,
            config
        );

        expect(graphs.hasPartialPatterns).to.equal(true);
        expect(Object.keys(graphs.partialInputPatterns)).to.eql(['type']);
        expect(Object.keys(graphs.partialOutputPatterns)).to.eql(['type']);
        expect(graphs.partialInputPatterns.type.n_clicks).to.have.lengthOf(1);
        expect(graphs.partialOutputPatterns.type.children).to.have.lengthOf(1);
        expect(graphs.partialInputPatterns['index,type']).to.equal(undefined);
    });
});

describe('dependencies — MATCH trigger resolvedId (#2462)', () => {
    it('getAnyVals picks MATCH values from trigger id', () => {
        // Use the same object reference for MATCH that the module uses
        // internally by exercising computeGraphs first.
        const errors = [];
        const graphs = computeGraphs(
            [
                {
                    output: 'out.children',
                    inputs: [{id: '{"id":["MATCH"]}', property: 'n_clicks'}],
                    state: [],
                    no_output: false
                }
            ],
            (m, l) => errors.push({m, l}),
            config
        );
        expect(errors).to.eql([]);
        const pattern = graphs.inputPatterns.id.n_clicks[0];
        const anyVals = getAnyVals(pattern.values, ['btn-1']);
        expect(anyVals).to.equal('["btn-1"]');
    });

    it('fires distinct callbacks per MATCH trigger when Output is fixed', () => {
        const errors = [];
        const graphs = computeGraphs(
            [
                {
                    output: 'out.children',
                    inputs: [{id: '{"id":["MATCH"]}', property: 'n_clicks'}],
                    state: [],
                    no_output: false
                }
            ],
            (m, l) => errors.push({m, l}),
            config
        );
        expect(errors).to.eql([]);

        const paths = makePaths(['out'], {
            id: [['btn-1'], ['btn-2']]
        });

        const first = getCallbacksByInput(
            graphs,
            paths,
            {id: 'btn-1'},
            'n_clicks',
            undefined,
            false
        );
        const second = getCallbacksByInput(
            graphs,
            paths,
            {id: 'btn-2'},
            'n_clicks',
            undefined,
            false
        );

        expect(first).to.have.lengthOf(1);
        expect(second).to.have.lengthOf(1);
        expect(first[0].resolvedId).to.not.equal(second[0].resolvedId);
        expect(first[0].resolvedId).to.include('btn-1');
        expect(second[0].resolvedId).to.include('btn-2');
    });
});

describe('dependencies: getUnfilteredLayoutCallbacks with a Patch (#3938)', () => {
    // Create a layout with two elements
    //      num: Input which patch writes to `value` directly
    //      badge: Output which `children` are written to, but unchanged by the patch

    // A callback listens to Input(num.value) and writes Output(badge.children)
    // Both the input and the output live inside the same patched chunk
    function makeGraphsAndPaths() {
        const errors = [];
        const graphs = computeGraphs(
            [
                {
                    output: 'badge.children',
                    inputs: [{id: 'num', property: 'value'}],
                    state: [],
                    no_output: false
                }
            ],
            (m, l) => errors.push({m, l}),
            config
        );
        expect(errors).to.eql([]);
        const paths = makePaths(['container', 'num', 'badge']);
        const layoutChunk = {
            props: {
                id: 'container',
                children: [
                    {props: {id: 'num', value: 100}},
                    {props: {id: 'badge', children: 'badge: stale'}}
                ]
            }
        };
        return {graphs, paths, layoutChunk};
    }

    it('keeps a callback alive when the patch wrote its Input directly, even though its Output was carried over', () => {
        const {graphs, paths, layoutChunk} = makeGraphsAndPaths();

        const patchAnalysis = {
            patchedProps: {children: true},
            freshIds: {},
            writtenProps: {num: {value: true}}
        };

        const callbacks = getUnfilteredLayoutCallbacks(
            graphs,
            paths,
            layoutChunk,
            {chunkPath: ['props', 'children'], patchAnalysis}
        );

        expect(callbacks).to.have.lengthOf(1);
        expect(callbacks[0].resolvedId).to.equal('badge.children');
    });

    it('still drops a carried over callback when neither its Input nor Output was touched by the patch', () => {
        const {graphs, paths, layoutChunk} = makeGraphsAndPaths();

        const patchAnalysis = {
            patchedProps: {children: true},
            freshIds: {},
            writtenProps: {}
        };

        const callbacks = getUnfilteredLayoutCallbacks(
            graphs,
            paths,
            layoutChunk,
            {chunkPath: ['props', 'children'], patchAnalysis}
        );

        expect(callbacks).to.have.lengthOf(0);
    });

    it('still runs the callback via its Output when the Output component is fresh', () => {
        const {graphs, paths, layoutChunk} = makeGraphsAndPaths();

        const patchAnalysis = {
            patchedProps: {children: true},
            freshIds: {badge: true},
            writtenProps: {}
        };

        const callbacks = getUnfilteredLayoutCallbacks(
            graphs,
            paths,
            layoutChunk,
            {chunkPath: ['props', 'children'], patchAnalysis}
        );

        expect(callbacks).to.have.lengthOf(1);
        expect(callbacks[0].resolvedId).to.equal('badge.children');
    });
});
