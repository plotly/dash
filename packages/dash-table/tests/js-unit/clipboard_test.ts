import {expect} from 'chai';
import * as R from 'ramda';

import applyClipboardToData from 'dash-table/utils/applyClipboardToData';

describe('clipboard', () => {
    const columns = ['c1'].map(id => ({
        id: id,
        name: id,
        editable: true,
        sort_as_null: []
    }));

    describe('with hidden columns', () => {
        const altColumns = ['c1', 'c2'].map(id => ({
            id: id,
            name: id,
            editable: true,
            sort_as_null: []
        }));

        describe('with column overflow', () => {
            it('returns all columns, 1st column visible only', () => {
                const altVisibleColumns = altColumns.slice(0, 1);

                const res = applyClipboardToData(
                    R.range(0, 2).map(value => [`${value}`, `${value + 1}`]),
                    {row: 0, column: 0, column_id: ''},
                    R.range(0, 1),
                    altColumns,
                    altVisibleColumns,
                    R.range(0, 1).map(() => ({c1: 'c1', c2: 'c2'})),
                    true,
                    true
                );

                expect(res).to.not.equal(undefined);

                if (res) {
                    expect(res.data.length).to.equal(2);
                    expect(Object.entries(res.data[0]).length).to.equal(3);
                    expect(res.columns.length).to.equal(3);
                    expect(res.columns[0].id).to.equal('c1');
                    expect(res.columns[2].id).to.equal('c2');
                }
            });
        });

        it('returns all columns, 2nd column visible only', () => {
            const altVisibleColumns = altColumns.slice(-1);

            const res = applyClipboardToData(
                R.range(0, 2).map(value => [`${value}`, `${value + 1}`]),
                {row: 0, column: 0, column_id: ''},
                R.range(0, 1),
                altColumns,
                altVisibleColumns,
                R.range(0, 1).map(() => ({c1: 'c1', c2: 'c2'})),
                true,
                true
            );

            expect(res).to.not.equal(undefined);

            if (res) {
                expect(res.data.length).to.equal(2);
                expect(Object.entries(res.data[0]).length).to.equal(3);
                expect(res.columns.length).to.equal(3);
                expect(res.columns[0].id).to.equal('c1');
                expect(res.columns[1].id).to.equal('c2');
            }
        });
    });

    describe('with column/row overflow allowed', () => {
        it('pastes one line at [0, 0] in one line df', () => {
            const res = applyClipboardToData(
                R.range(0, 1).map(value => [`${value}`]),
                {row: 0, column: 0, column_id: ''},
                R.range(0, 1),
                columns,
                columns,
                R.range(0, 1).map(() => ({c1: 'c1'})),
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
                columns,
                columns,
                R.range(0, 1).map(() => ({c1: 'c1'})),
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
                columns,
                columns,
                R.range(0, 3).map(() => ({c1: 'c1'})),
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
                columns,
                columns,
                R.range(0, 3).map(() => ({c1: 'c1'})),
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
                columns,
                columns,
                R.range(0, 1).map(() => ({c1: 'c1'})),
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
                columns,
                columns,
                R.range(0, 1).map(() => ({c1: 'c1'})),
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
                columns,
                columns,
                R.range(0, 3).map(() => ({c1: 'c1'})),
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
                columns,
                columns,
                R.range(0, 3).map(() => ({c1: 'c1'})),
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
