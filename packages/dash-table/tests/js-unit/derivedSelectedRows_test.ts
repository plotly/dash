import {expect} from 'chai';
import * as R from 'ramda';

import derivedSelectedRows from 'dash-table/derived/selects/rows';

describe('derived selected rows', () => {
    let derive = derivedSelectedRows();

    beforeEach(() => {
        derive = derivedSelectedRows();
    });

    describe('with dense derived indices', () => {
        const indices = R.range(0, 10);

        it('when all rows are selected', () => {
            const result = derive(indices, indices);

            expect(result.length).to.equal(indices.length);
            R.forEach(index => expect(result[index]).to.equal(index), result);
        });

        it('when some rows are selected', () => {
            const selected = [0, 2, 4];
            const result = derive(indices, selected);

            expect(result.length).to.equal(selected.length);
            R.forEach(
                index => expect(result[index]).to.equal(selected[index]),
                result
            );
        });

        it('when derived indices are shifted', () => {
            const shiftedIndices = R.range(2, 12);
            const result = derive(shiftedIndices, shiftedIndices);

            expect(result.length).to.equal(shiftedIndices.length);
            R.forEach(index => expect(result[index]).to.equal(index), result);
        });

        it('when derived indices are shifted and negative', () => {
            const shiftedIndices = R.range(-10, 10);
            const result = derive(shiftedIndices, shiftedIndices);

            expect(result.length).to.equal(shiftedIndices.length);
            R.forEach(index => expect(result[index]).to.equal(index), result);
        });

        it('when no row is selected', () => {
            const result = derive(indices, []);

            expect(result.length).to.equal(0);
        });

        it('when out-of-scope row is selected', () => {
            const selected = [0, indices.length];
            const result = derive(indices, selected);

            expect(result.length).to.equal(1);
            expect(result[0]).to.equal(0);
        });
    });

    describe('with sparse derived indices', () => {
        const indices = R.map(i => i * 2, R.range(0, 10));

        it('when all rows are selected', () => {
            const result = derive(indices, indices);

            expect(result.length).to.equal(indices.length);
            R.forEach(index => expect(result[index]).to.equal(index), result);
        });

        it('when some rows are selected', () => {
            const selected = [0, 2, 4];
            const result = derive(indices, selected);

            expect(result.length).to.equal(selected.length);
            R.forEach(
                index => expect(result[index]).to.equal(selected[index] / 2),
                result
            );
        });

        it('when derived indices are shifted', () => {
            const shiftedIndices = R.map(i => i * 2, R.range(2, 12));
            const result = derive(shiftedIndices, shiftedIndices);

            expect(result.length).to.equal(shiftedIndices.length);
            R.forEach(index => expect(result[index]).to.equal(index), result);
        });

        it('when derived indices are shifted and negative', () => {
            const shiftedIndices = R.map(i => i * 2, R.range(-10, 10));
            const result = derive(shiftedIndices, shiftedIndices);

            expect(result.length).to.equal(shiftedIndices.length);
            R.forEach(index => expect(result[index]).to.equal(index), result);
        });

        it('when no row is selected', () => {
            const result = derive(indices, []);

            expect(result.length).to.equal(0);
        });

        it('when out-of-scope row is selected', () => {
            const selected = [0, 1, Number.MAX_SAFE_INTEGER];
            const result = derive(indices, selected);

            expect(result.length).to.equal(1);
            expect(result[0]).to.equal(0);
        });
    });
});
