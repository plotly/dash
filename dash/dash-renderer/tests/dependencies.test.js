import {expect} from 'chai';
import {beforeEach, describe, it} from 'mocha';
import {computeGraphs, getAnyVals} from '../src/actions/dependencies';
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
