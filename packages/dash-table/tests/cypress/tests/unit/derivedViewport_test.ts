import * as R from 'ramda';

import derivedViewportDataframe from 'dash-table/derived/dataframe/viewport';

describe('derived viewport', () => {
    const viewportDataframe = derivedViewportDataframe();

    describe('virtual dataframe <= page size', () => {
        describe('with no pagination', () => {
            it('returns entire dataframe', () => {
                const result = viewportDataframe(
                    false,
                    { displayed_pages: 1, current_page: 0, page_size: 250 },
                    R.map(() => { }, R.range(0, 5)),
                    R.range(0, 5)
                );

                expect(result.dataframe.length).to.equal(5);
                expect(result.indices.length).to.equal(5);
            });
        });

        describe('with fe pagination', () => {
            it('returns entire dataframe', () => {
                const result = viewportDataframe(
                    'fe',
                    { displayed_pages: 1, current_page: 0, page_size: 250 },
                    R.map(() => { }, R.range(0, 5)),
                    R.range(0, 5)
                );

                expect(result.dataframe.length).to.equal(5);
                expect(result.indices.length).to.equal(5);
            });
        });

        describe('with be pagination', () => {
            it('returns entire dataframe', () => {
                const result = viewportDataframe(
                    'be',
                    { displayed_pages: 1, current_page: 0, page_size: 250 },
                    R.map(() => { }, R.range(0, 5)),
                    R.range(0, 5)
                );

                expect(result.dataframe.length).to.equal(5);
                expect(result.indices.length).to.equal(5);
            });
        });
    });

    describe('virtual dataframe > page size', () => {
        describe('with fe pagination', () => {
            it('returns slice of dataframe', () => {
                const result = viewportDataframe(
                    'fe',
                    { displayed_pages: 1, current_page: 0, page_size: 250 },
                    R.map(idx => ({ idx }), R.range(0, 500)),
                    R.range(0, 500)
                );

                expect(result.dataframe.length).to.equal(250);
                expect(result.indices.length).to.equal(250);
                expect(result.dataframe[0].idx).to.equal(0);
                expect(result.dataframe[249].idx).to.equal(249);
                expect(result.indices[0]).to.equal(0);
                expect(result.indices[249]).to.equal(249);
            });
        });
    });
});