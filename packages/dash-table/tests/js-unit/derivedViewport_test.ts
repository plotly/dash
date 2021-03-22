import {expect} from 'chai';
import * as R from 'ramda';

import derivedViewportData from 'dash-table/derived/data/viewport';
import {TableAction} from 'dash-table/components/Table/props';

describe('derived viewport', () => {
    const viewportData = derivedViewportData();

    describe('virtual data <= page size', () => {
        describe('with no pagination', () => {
            it('returns entire data', () => {
                const result = viewportData(
                    TableAction.None,
                    0,
                    250,
                    R.map(() => {}, R.range(0, 5)),
                    R.range(0, 5)
                );

                expect(result.data.length).to.equal(5);
                expect(result.indices.length).to.equal(5);
            });
        });

        describe('with fe pagination', () => {
            it('returns entire data', () => {
                const result = viewportData(
                    TableAction.Native,
                    0,
                    250,
                    R.map(() => {}, R.range(0, 5)),
                    R.range(0, 5)
                );

                expect(result.data.length).to.equal(5);
                expect(result.indices.length).to.equal(5);
            });
        });

        describe('with be pagination', () => {
            it('returns entire data', () => {
                const result = viewportData(
                    TableAction.Custom,
                    0,
                    250,
                    R.map(() => {}, R.range(0, 5)),
                    R.range(0, 5)
                );

                expect(result.data.length).to.equal(5);
                expect(result.indices.length).to.equal(5);
            });
        });
    });

    describe('virtual data > page size', () => {
        describe('with fe pagination', () => {
            it('returns slice of data', () => {
                const result = viewportData(
                    TableAction.Native,
                    0,
                    250,
                    R.map(idx => ({idx}), R.range(0, 500)),
                    R.range(0, 500)
                );

                expect(result.data.length).to.equal(250);
                expect(result.indices.length).to.equal(250);
                expect(result.data[0].idx).to.equal(0);
                expect(result.data[249].idx).to.equal(249);
                expect(result.indices[0]).to.equal(0);
                expect(result.indices[249]).to.equal(249);
            });
        });
    });
});
