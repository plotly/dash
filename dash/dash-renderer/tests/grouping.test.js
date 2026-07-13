import {expect} from 'chai';
import {describe, it} from 'mocha';
import {mapGrouping, flattenGroupingByIndex} from '../src/utils/grouping';

describe('grouping utils (clientside flexible signatures)', () => {
    describe('mapGrouping', () => {
        it('maps a scalar grouping', () => {
            expect(mapGrouping(i => i * 10, 2)).to.equal(20);
        });

        it('maps a flat list grouping', () => {
            expect(mapGrouping(i => i * 10, [0, 1, 2])).to.deep.equal([
                0, 10, 20
            ]);
        });

        it('maps a dict grouping', () => {
            expect(mapGrouping(i => i * 10, {a: 0, b: 1})).to.deep.equal({
                a: 0,
                b: 10
            });
        });

        it('maps a nested mixed grouping', () => {
            expect(
                mapGrouping(i => i * 10, {a: [0, 1], b: {c: 2}})
            ).to.deep.equal({a: [0, 10], b: {c: 20}});
        });
    });

    describe('flattenGroupingByIndex', () => {
        it('round-trips with mapGrouping', () => {
            const indices = {a: [0, 2], b: {c: 1}};
            const flat = ['x', 'y', 'z'];
            const grouped = mapGrouping(i => flat[i], indices);
            expect(flattenGroupingByIndex(indices, grouped, 3)).to.deep.equal(
                flat
            );
        });

        it('flattens a scalar grouping', () => {
            expect(flattenGroupingByIndex(0, 'val', 1)).to.deep.equal(['val']);
        });

        it('flattens a dict grouping with reordered indices', () => {
            // Mixed Input/State: {a: Input, s: State, b: Input} -> {a: 0, s: 2, b: 1}
            expect(
                flattenGroupingByIndex(
                    {a: 0, s: 2, b: 1},
                    {a: 'A', s: 'S', b: 'B'},
                    3
                )
            ).to.deep.equal(['A', 'B', 'S']);
        });

        it('preserves array and object leaf values', () => {
            const noUpdate = {description: 'no_update sentinel'};
            const flat = flattenGroupingByIndex(
                {a: 0, b: 1},
                {a: [1, 2, 3], b: noUpdate},
                2
            );
            expect(flat[0]).to.deep.equal([1, 2, 3]);
            expect(flat[1]).to.equal(noUpdate);
        });

        it('throws on wrong array length', () => {
            expect(() =>
                flattenGroupingByIndex([0, 1], ['only-one'], 2)
            ).to.throw(/length 2/);
        });

        it('throws on non-array value for array schema', () => {
            expect(() => flattenGroupingByIndex([0, 1], 'nope', 2)).to.throw(
                /Expected an array/
            );
        });

        it('throws on missing dict keys', () => {
            expect(() =>
                flattenGroupingByIndex({a: 0, b: 1}, {a: 'A'}, 2)
            ).to.throw(/keys/);
        });

        it('throws on extra dict keys', () => {
            expect(() =>
                flattenGroupingByIndex({a: 0}, {a: 'A', b: 'B'}, 1)
            ).to.throw(/keys/);
        });

        it('throws on non-object value for dict schema', () => {
            expect(() => flattenGroupingByIndex({a: 0}, ['A'], 1)).to.throw(
                /Expected an object/
            );
        });

        it('reports the path of a nested mismatch', () => {
            expect(() =>
                flattenGroupingByIndex({a: [0, 1]}, {a: [1]}, 2)
            ).to.throw(/\["a"\]/);
        });
    });
});
