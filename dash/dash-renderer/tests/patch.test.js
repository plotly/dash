import {expect} from 'chai';
import {describe, it} from 'mocha';
import {handlePatch, parsePatchProps} from '../src/actions/patch';
import {
    analysisForAllProps,
    analysisForProp,
    createPatchAnalysis,
    isCarriedOverByPatch,
    isUntouchedByPatch,
    tailAppendCount
} from '../src/actions/patchAnalysis';
import {stringifyId} from '../src/actions/dependencies';

const component = (id, props = {}) => ({
    namespace: 'dash_html_components',
    type: 'Div',
    props: {id, ...props}
});

const patch = (...operations) => ({
    __dash_patch_update: '__dash_patch_update',
    operations
});

describe('patch analysis, what a Patch changed', () => {
    it('reports appended components as created, existing ones as carried over', () => {
        const analysis = createPatchAnalysis();
        const children = [component('kept', {value: 'edited'})];

        const result = handlePatch(
            children,
            patch({
                operation: 'Append',
                location: [],
                params: {value: component('added')}
            }),
            analysis
        );

        expect(result).to.have.lengthOf(2);
        expect(analysis.freshIds).to.deep.equal({added: true});
        expect(isCarriedOverByPatch(analysis, 'added')).to.equal(false);
        expect(isCarriedOverByPatch(analysis, 'kept')).to.equal(true);
        expect(isUntouchedByPatch(analysis, 'kept')).to.equal(true);
    });

    it('reports components rebuilt with a reused id as created', () => {
        const analysis = createPatchAnalysis();
        const children = [component('reused', {value: 'edited'})];

        const result = handlePatch(
            children,
            patch(
                {operation: 'Clear', location: [], params: {}},
                {
                    operation: 'Append',
                    location: [],
                    params: {value: component('reused', {value: 'initial'})}
                }
            ),
            analysis
        );

        expect(result).to.have.lengthOf(1);
        expect(analysis.freshIds).to.deep.equal({reused: true});
        expect(isCarriedOverByPatch(analysis, 'reused')).to.equal(false);
        expect(isUntouchedByPatch(analysis, 'reused')).to.equal(false);
    });

    it('does not report the containers assocPath had to rebuild as created', () => {
        const analysis = createPatchAnalysis();
        const children = [
            component('row', {
                children: [component('input', {value: 'edited'})]
            })
        ];

        handlePatch(
            children,
            patch({
                operation: 'Assign',
                location: [0, 'props', 'children', 0, 'props', 'value'],
                params: {value: 'server'}
            }),
            analysis
        );

        expect(analysis.freshIds).to.deep.equal({});
        expect(analysis.writtenProps).to.deep.equal({input: {value: true}});
        // The container between the patched prop and the changed value gets a
        // new props object, but the patch did not create it
        expect(isCarriedOverByPatch(analysis, 'row')).to.equal(true);
        expect(isUntouchedByPatch(analysis, 'row')).to.equal(true);
        // The component the patch wrote on is not new either, but persistence
        // still has to look at it to notice the server override
        expect(isCarriedOverByPatch(analysis, 'input')).to.equal(true);
        expect(isUntouchedByPatch(analysis, 'input')).to.equal(false);
    });

    it('records the written prop of a merge on an existing component', () => {
        const analysis = createPatchAnalysis();
        const children = [component('input', {value: 'edited'})];

        handlePatch(
            children,
            patch({
                operation: 'Merge',
                location: [0, 'props'],
                params: {value: {value: 'server', className: 'c'}}
            }),
            analysis
        );

        expect(analysis.freshIds).to.deep.equal({});
        expect(analysis.writtenProps).to.deep.equal({
            input: {value: true, className: true}
        });
    });

    it('collects nested and wildcard ids of created components', () => {
        const analysis = createPatchAnalysis();
        const wildcardId = {type: 'row', index: 2};

        handlePatch(
            [],
            patch({
                operation: 'Append',
                location: [],
                params: {
                    value: component(wildcardId, {
                        children: [component('deep')]
                    })
                }
            }),
            analysis
        );

        expect(analysis.freshIds).to.deep.equal({
            [stringifyId(wildcardId)]: true,
            deep: true
        });
    });

    it('does not report removed components as created', () => {
        const analysis = createPatchAnalysis();
        const gone = component('gone');

        handlePatch(
            [component('kept'), gone],
            patch({operation: 'Remove', location: [], params: {value: gone}}),
            analysis
        );

        expect(analysis.freshIds).to.deep.equal({});
    });

    it('only describes the props that were patched', () => {
        const analysis = createPatchAnalysis();

        const props = parsePatchProps(
            {
                children: patch({
                    operation: 'Append',
                    location: [],
                    params: {value: component('added')}
                }),
                style: {color: 'red'}
            },
            {children: [component('kept')], style: {}},
            analysis
        );

        expect(props.children).to.have.lengthOf(2);
        expect(analysis.patchedProps).to.deep.equal({children: true});
        expect(analysisForProp(analysis, 'children')).to.equal(analysis);
        expect(analysisForProp(analysis, 'style')).to.equal(undefined);
        expect(analysisForAllProps(analysis, ['children'])).to.equal(analysis);
        expect(analysisForAllProps(analysis, ['children', 'style'])).to.equal(
            undefined
        );
    });

    it('treats every component as new without an analysis', () => {
        expect(isCarriedOverByPatch(undefined, 'anything')).to.equal(false);
        expect(isUntouchedByPatch(undefined, 'anything')).to.equal(false);
    });
});

describe('patch analysis, pure tail-append detection (perf fast-path gate)', () => {
    // These guard the O(appended) append fast-path: it may ONLY be taken when a
    // patch is exclusively tail Append/Extend ops on a given property, so that
    // pre-existing items are provably untouched. Any other op must disqualify it,
    // or the fast-path would skip work a real change needed.
    it('counts a single Append as one tail-append', () => {
        const analysis = createPatchAnalysis();
        parsePatchProps(
            {
                children: patch({
                    operation: 'Append',
                    location: [],
                    params: {value: component('added')}
                })
            },
            {children: [component('kept')]},
            analysis
        );
        expect(tailAppendCount(analysis, 'children')).to.equal(1);
    });

    it('counts Extend by the number of items added', () => {
        const analysis = createPatchAnalysis();
        parsePatchProps(
            {
                children: patch({
                    operation: 'Extend',
                    location: [],
                    params: {
                        value: [component('a'), component('b'), component('c')]
                    }
                })
            },
            {children: [component('kept')]},
            analysis
        );
        expect(tailAppendCount(analysis, 'children')).to.equal(3);
    });

    it('accumulates multiple appends in one patch', () => {
        const analysis = createPatchAnalysis();
        parsePatchProps(
            {
                children: patch(
                    {
                        operation: 'Append',
                        location: [],
                        params: {value: component('a')}
                    },
                    {
                        operation: 'Append',
                        location: [],
                        params: {value: component('b')}
                    }
                )
            },
            {children: [component('kept')]},
            analysis
        );
        expect(tailAppendCount(analysis, 'children')).to.equal(2);
    });

    it('disqualifies the property when a Prepend is mixed in', () => {
        const analysis = createPatchAnalysis();
        parsePatchProps(
            {
                children: patch(
                    {
                        operation: 'Append',
                        location: [],
                        params: {value: component('a')}
                    },
                    {
                        operation: 'Prepend',
                        location: [],
                        params: {value: component('z')}
                    }
                )
            },
            {children: [component('kept')]},
            analysis
        );
        // Prepend shifts existing indices -> NOT a pure tail append.
        expect(tailAppendCount(analysis, 'children')).to.equal(0);
    });

    it('disqualifies the property when an Insert is mixed in', () => {
        const analysis = createPatchAnalysis();
        parsePatchProps(
            {
                children: patch(
                    {
                        operation: 'Append',
                        location: [],
                        params: {value: component('a')}
                    },
                    {
                        operation: 'Insert',
                        location: [],
                        params: {index: 0, value: component('z')}
                    }
                )
            },
            {children: [component('kept')]},
            analysis
        );
        expect(tailAppendCount(analysis, 'children')).to.equal(0);
    });

    it('disqualifies the property when a Delete is mixed in', () => {
        const analysis = createPatchAnalysis();
        parsePatchProps(
            {
                children: patch(
                    {
                        operation: 'Append',
                        location: [],
                        params: {value: component('a')}
                    },
                    {operation: 'Delete', location: [0], params: {}}
                )
            },
            {children: [component('kept'), component('kept2')]},
            analysis
        );
        expect(tailAppendCount(analysis, 'children')).to.equal(0);
    });

    it('disqualifies when an append writes at a nested (non-top) location', () => {
        const analysis = createPatchAnalysis();
        parsePatchProps(
            {
                children: patch({
                    operation: 'Append',
                    location: [0, 'props', 'children'],
                    params: {value: component('a')}
                })
            },
            {children: [component('kept', {children: []})]},
            analysis
        );
        // Appending into a child's children is not a top-level tail append.
        expect(tailAppendCount(analysis, 'children')).to.equal(0);
    });

    it('reports 0 for a property that saw no patch and without an analysis', () => {
        const analysis = createPatchAnalysis();
        expect(tailAppendCount(analysis, 'children')).to.equal(0);
        expect(tailAppendCount(undefined, 'children')).to.equal(0);
    });
});
