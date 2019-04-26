import * as R from 'ramda';

import applyClipboardToData from 'dash-table/utils/applyClipboardToData';

describe('clipboard', () => {
    describe('with column/row overflow allowed', () => {
        it('pastes one line at [0, 0] in one line df', () => {
            const res = applyClipboardToData(
                R.range(0, 1).map(value => [`${value}`]),
                {row: 0, column: 0, column_id: ''},
                R.range(0, 1),
                ['c1'].map(id => ({ id: id, name: id })),
                R.range(0, 1).map(() => ({ c1: 'c1' })),
                true,
                true
            );

            expect(res).to.not.equal(undefined);

            if (res) {
                expect(res.data.length).to.equal(1);
                expect(res.data[0].c1).to.equal('0');
            }
        });

        it('pastes two lines at [0, 0] in one line df', () => {
            const res = applyClipboardToData(
                R.range(0, 2).map(value => [`${value}`]),
                {row: 0, column: 0, column_id: ''},
                R.range(0, 1),
                ['c1'].map(id => ({ id: id, name: id })),
                R.range(0, 1).map(() => ({ c1: 'c1' })),
                true,
                true
            );

            expect(res).to.not.equal(undefined);

            if (res) {
                expect(res.data.length).to.equal(2);
                expect(res.data[0].c1).to.equal('0');
                expect(res.data[1].c1).to.equal('1');
            }
        });

        it('pastes ten lines at [0, 0] in three line df', () => {
            const res = applyClipboardToData(
                R.range(0, 10).map(value => [`${value}`]),
                {row: 0, column: 0, column_id: ''},
                R.range(0, 3),
                ['c1'].map(id => ({ id: id, name: id })),
                R.range(0, 3).map(() => ({ c1: 'c1' })),
                true,
                true
            );

            expect(res).to.not.equal(undefined);

            if (res) {
                expect(res.data.length).to.equal(10);
                for (let i = 0; i < 10; ++i) {
                    expect(res.data[i].c1).to.equal(`${i}`);
                }
            }
        });

        it('pastes ten lines at [1, 0] in three line df', () => {
            const res = applyClipboardToData(
                R.range(0, 10).map(value => [`${value}`]),
                {row: 1, column: 0, column_id: ''},
                R.range(0, 3),
                ['c1'].map(id => ({ id: id, name: id })),
                R.range(0, 3).map(() => ({ c1: 'c1' })),
                true,
                true
            );

            expect(res).to.not.equal(undefined);

            if (res) {
                expect(res.data.length).to.equal(11);
                expect(res.data[0].c1).to.equal('c1');
                for (let i = 0; i < 10; ++i) {
                    expect(res.data[i + 1].c1).to.equal(`${i}`);
                }
            }
        });
    });

    describe('with column overflow allowed, row overflow not allowed', () => {
        it('pastes one line at [0, 0] in one line df', () => {
            const res = applyClipboardToData(
                R.range(0, 1).map(value => [`${value}`]),
                {row: 0, column: 0, column_id: ''},
                R.range(0, 1),
                ['c1'].map(id => ({ id: id, name: id })),
                R.range(0, 1).map(() => ({ c1: 'c1' })),
                true,
                false
            );

            expect(res).to.not.equal(undefined);

            if (res) {
                expect(res.data.length).to.equal(1);
                expect(res.data[0].c1).to.equal('0');
            }
        });

        it('pastes two lines at [0, 0] in one line df', () => {
            const res = applyClipboardToData(
                R.range(0, 2).map(value => [`${value}`]),
                {row: 0, column: 0, column_id: ''},
                R.range(0, 1),
                ['c1'].map(id => ({ id: id, name: id })),
                R.range(0, 1).map(() => ({ c1: 'c1' })),
                true,
                false
            );

            expect(res).to.not.equal(undefined);

            if (res) {
                expect(res.data.length).to.equal(1);
                expect(res.data[0].c1).to.equal('0');
            }
        });

        it('pastes ten lines at [0, 0] in three line df', () => {
            const res = applyClipboardToData(
                R.range(0, 10).map(value => [`${value}`]),
                {row: 0, column: 0, column_id: ''},
                R.range(0, 3),
                ['c1'].map(id => ({ id: id, name: id })),
                R.range(0, 3).map(() => ({ c1: 'c1' })),
                true,
                false
            );

            expect(res).to.not.equal(undefined);

            if (res) {
                expect(res.data.length).to.equal(3);
                for (let i = 0; i < 3; ++i) {
                    expect(res.data[i].c1).to.equal(`${i}`);
                }
            }
        });

        it('pastes ten lines at [1, 0] in three line df', () => {
            const res = applyClipboardToData(
                R.range(0, 10).map(value => [`${value}`]),
                {row: 1, column: 0, column_id: ''},
                R.range(0, 3),
                ['c1'].map(id => ({ id: id, name: id })),
                R.range(0, 3).map(() => ({ c1: 'c1' })),
                true,
                false
            );

            expect(res).to.not.equal(undefined);

            if (res) {
                expect(res.data.length).to.equal(3);
                expect(res.data[0].c1).to.equal('c1');
                for (let i = 0; i < 2; ++i) {
                    expect(res.data[i + 1].c1).to.equal(`${i}`);
                }
            }
        });
    });
});
