import {expect} from 'chai';
import * as R from 'ramda';

import sort, {SortDirection, SortBy} from 'core/sorting';
import multiUpdate from 'core/sorting/multi';
import singleUpdate from 'core/sorting/single';

describe('sort', () => {
    it('sorts', () => {
        const data = [1, 3, 4, 2].map(v => ({a: v}));
        const sorted = sort(data, [
            {column_id: 'a', direction: SortDirection.Descending}
        ]);

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0].a).to.equal(4);
        expect(sorted[1].a).to.equal(3);
        expect(sorted[2].a).to.equal(2);
        expect(sorted[3].a).to.equal(1);
    });

    it('sorts undefined after when descending', () => {
        const data = [1, undefined, 3, undefined, 4, 2, undefined].map(v => ({
            a: v
        }));
        const sorted = sort(data, [
            {column_id: 'a', direction: SortDirection.Descending}
        ]);

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0].a).to.equal(4);
        expect(sorted[1].a).to.equal(3);
        expect(sorted[2].a).to.equal(2);
        expect(sorted[3].a).to.equal(1);
        expect(sorted[4].a).to.equal(undefined);
        expect(sorted[5].a).to.equal(undefined);
        expect(sorted[6].a).to.equal(undefined);
    });

    it('sorts undefined after when ascending', () => {
        const data = [1, undefined, 3, undefined, 4, 2, undefined].map(v => ({
            a: v
        }));
        const sorted = sort(data, [
            {column_id: 'a', direction: SortDirection.Ascending}
        ]);

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0].a).to.equal(1);
        expect(sorted[1].a).to.equal(2);
        expect(sorted[2].a).to.equal(3);
        expect(sorted[3].a).to.equal(4);
        expect(sorted[4].a).to.equal(undefined);
        expect(sorted[5].a).to.equal(undefined);
        expect(sorted[6].a).to.equal(undefined);
    });

    it('sorts null after when descending', () => {
        const data = [1, null, 3, null, 4, 2, null].map(v => ({a: v}));
        const sorted = sort(data, [
            {column_id: 'a', direction: SortDirection.Descending}
        ]);

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0].a).to.equal(4);
        expect(sorted[1].a).to.equal(3);
        expect(sorted[2].a).to.equal(2);
        expect(sorted[3].a).to.equal(1);
        expect(sorted[4].a).to.equal(null);
        expect(sorted[5].a).to.equal(null);
        expect(sorted[6].a).to.equal(null);
    });

    it('sorts null after when ascending', () => {
        const data = [1, null, 3, null, 4, 2, null].map(v => ({a: v}));
        const sorted = sort(data, [
            {column_id: 'a', direction: SortDirection.Ascending}
        ]);

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0].a).to.equal(1);
        expect(sorted[1].a).to.equal(2);
        expect(sorted[2].a).to.equal(3);
        expect(sorted[3].a).to.equal(4);
        expect(sorted[4].a).to.equal(null);
        expect(sorted[5].a).to.equal(null);
        expect(sorted[6].a).to.equal(null);
    });

    it('sorts nully (undefined, null, 0, 1) after when descending', () => {
        const data = [1, 0, 3, undefined, 4, 2, null].map(v => ({a: v}));
        const sorted = sort(
            data,
            [{column_id: 'a', direction: SortDirection.Ascending}],
            value => R.isNil(value) || value === 0 || value === 1
        );

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0].a).to.equal(2);
        expect(sorted[1].a).to.equal(3);
        expect(sorted[2].a).to.equal(4);
    });

    it('sorts nully (undefined, null, 0, 1) after when ascending', () => {
        const data = [1, 0, 3, undefined, 4, 2, null].map(v => ({a: v}));
        const sorted = sort(
            data,
            [{column_id: 'a', direction: SortDirection.Descending}],
            value => R.isNil(value) || value === 0 || value === 1
        );

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0].a).to.equal(4);
        expect(sorted[1].a).to.equal(3);
        expect(sorted[2].a).to.equal(2);
    });

    it('respects sort order - 1', () => {
        const data = [
            {a: 1, b: 3},
            {a: 2, b: 3},
            {a: 0, b: 0},
            {a: 0, b: 3},
            {a: 0, b: 1},
            {a: 2, b: 1},
            {a: 1, b: 0},
            {a: 1, b: 1},
            {a: 2, b: 0}
        ];

        const sorted = sort(data, [
            {column_id: 'a', direction: SortDirection.Descending},
            {column_id: 'b', direction: SortDirection.Descending}
        ]);

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0].a).to.equal(2);
        expect(sorted[0].b).to.equal(3);
        expect(sorted[1].a).to.equal(2);
        expect(sorted[1].b).to.equal(1);
        expect(sorted[2].a).to.equal(2);
        expect(sorted[2].b).to.equal(0);
    });

    it('respects sort order - 2', () => {
        const data = [
            {a: 1, b: 3},
            {a: 2, b: 3},
            {a: 0, b: 0},
            {a: 0, b: 3},
            {a: 0, b: 1},
            {a: 2, b: 1},
            {a: 1, b: 0},
            {a: 1, b: 1},
            {a: 2, b: 0}
        ];

        const sorted = sort(data, [
            {column_id: 'b', direction: SortDirection.Descending},
            {column_id: 'a', direction: SortDirection.Ascending}
        ]);

        expect(sorted.length).to.equal(data.length);
        expect(sorted[0].a).to.equal(0);
        expect(sorted[0].b).to.equal(3);
        expect(sorted[1].a).to.equal(1);
        expect(sorted[1].b).to.equal(3);
        expect(sorted[2].a).to.equal(2);
        expect(sorted[2].b).to.equal(3);
    });
});

describe('sorting settings', () => {
    describe('single column sorting', () => {
        it('new descending', () => {
            const settings = singleUpdate([], {
                column_id: 'a',
                direction: SortDirection.Descending
            });

            expect(settings.length).to.equal(1);
            expect(settings[0].column_id).to.equal('a');
            expect(settings[0].direction).to.equal(SortDirection.Descending);
        });

        it('update to descending', () => {
            const settings = singleUpdate(
                [{column_id: 'a', direction: SortDirection.Ascending}],
                {column_id: 'a', direction: SortDirection.Descending}
            );

            expect(settings.length).to.equal(1);
            expect(settings[0].column_id).to.equal('a');
            expect(settings[0].direction).to.equal(SortDirection.Descending);
        });

        it('remove by setting to None', () => {
            const settings = singleUpdate(
                [{column_id: 'a', direction: SortDirection.Ascending}],
                {column_id: 'a', direction: SortDirection.None}
            );

            expect(settings.length).to.equal(0);
        });

        it('replace with other', () => {
            const settings = singleUpdate(
                [{column_id: 'a', direction: SortDirection.Ascending}],
                {column_id: 'b', direction: SortDirection.Ascending}
            );

            expect(settings.length).to.equal(1);
            expect(settings[0].column_id).to.equal('b');
            expect(settings[0].direction).to.equal(SortDirection.Ascending);
        });

        it('replace with None', () => {
            const settings = singleUpdate(
                [{column_id: 'a', direction: SortDirection.Ascending}],
                {column_id: 'b', direction: SortDirection.None}
            );

            expect(settings.length).to.equal(0);
        });
    });

    describe('multi columns sorting', () => {
        it('new descending', () => {
            const settings = multiUpdate([], {
                column_id: 'a',
                direction: SortDirection.Descending
            });

            expect(settings.length).to.equal(1);
            expect(settings[0].column_id).to.equal('a');
            expect(settings[0].direction).to.equal(SortDirection.Descending);
        });

        it('update to descending', () => {
            const settings = multiUpdate(
                [{column_id: 'a', direction: SortDirection.Ascending}],
                {column_id: 'a', direction: SortDirection.Descending}
            );

            expect(settings.length).to.equal(1);
            expect(settings[0].column_id).to.equal('a');
            expect(settings[0].direction).to.equal(SortDirection.Descending);
        });

        it('remove by setting to None', () => {
            const settings = multiUpdate(
                [{column_id: 'a', direction: SortDirection.Ascending}],
                {column_id: 'a', direction: SortDirection.None}
            );

            expect(settings.length).to.equal(0);
        });

        it('respects order', () => {
            const settings = multiUpdate(
                [{column_id: 'a', direction: SortDirection.Ascending}],
                {column_id: 'b', direction: SortDirection.Ascending}
            );

            expect(settings.length).to.equal(2);
            expect(settings[0].column_id).to.equal('a');
            expect(settings[1].column_id).to.equal('b');
        });

        it('respects order when removed and added back', () => {
            let settings: SortBy = [
                {column_id: 'a', direction: SortDirection.Ascending}
            ];

            settings = multiUpdate(settings, {
                column_id: 'b',
                direction: SortDirection.Ascending
            });

            settings = multiUpdate(settings, {
                column_id: 'a',
                direction: SortDirection.None
            });

            settings = multiUpdate(settings, {
                column_id: 'a',
                direction: SortDirection.Ascending
            });

            expect(settings.length).to.equal(2);
            expect(settings[0].column_id).to.equal('b');
            expect(settings[1].column_id).to.equal('a');
        });
    });
});
