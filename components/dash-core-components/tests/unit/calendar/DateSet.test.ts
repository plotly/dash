import {DateSet} from '../../../src/utils/calendar/DateSet';

describe('DateSet', () => {
    describe('constructor', () => {
        it('creates empty DateSet with no arguments', () => {
            const dateSet = new DateSet();
            expect(dateSet.size).toBe(0);
        });

        it('creates DateSet from array of dates', () => {
            const dates = [
                new Date(2025, 0, 1),
                new Date(2025, 0, 2),
                new Date(2025, 0, 3),
            ];
            const dateSet = new DateSet(dates);

            expect(dateSet.size).toBe(3);
            expect(dateSet.has(new Date(2025, 0, 1))).toBe(true);
            expect(dateSet.has(new Date(2025, 0, 2))).toBe(true);
            expect(dateSet.has(new Date(2025, 0, 3))).toBe(true);
        });

        it('creates DateSet from another DateSet (copy constructor)', () => {
            const original = new DateSet([new Date(2025, 0, 1), new Date(2025, 0, 2)]);
            const copy = new DateSet(original);

            expect(copy.size).toBe(2);
            expect(copy.has(new Date(2025, 0, 1))).toBe(true);

            // Verify it's a copy, not a reference
            copy.add(new Date(2025, 0, 3));
            expect(copy.size).toBe(3);
            expect(original.size).toBe(2);
        });

        it('handles duplicate dates in array', () => {
            const dates = [
                new Date(2025, 0, 1),
                new Date(2025, 0, 1), // duplicate
                new Date(2025, 0, 2),
            ];
            const dateSet = new DateSet(dates);

            expect(dateSet.size).toBe(2); // duplicates removed
        });
    });

    describe('has()', () => {
        it('returns true for dates in the set', () => {
            const dateSet = new DateSet([new Date(2025, 0, 15)]);
            expect(dateSet.has(new Date(2025, 0, 15))).toBe(true);
        });

        it('returns false for dates not in the set', () => {
            const dateSet = new DateSet([new Date(2025, 0, 15)]);
            expect(dateSet.has(new Date(2025, 0, 16))).toBe(false);
        });

        it('normalizes dates to midnight for comparison', () => {
            const dateSet = new DateSet([new Date(2025, 0, 15, 14, 30)]);
            expect(dateSet.has(new Date(2025, 0, 15, 0, 0))).toBe(true);
            expect(dateSet.has(new Date(2025, 0, 15, 23, 59))).toBe(true);
        });
    });

    describe('add() and delete()', () => {
        it('adds a date to the set', () => {
            const dateSet = new DateSet();
            dateSet.add(new Date(2025, 0, 1));

            expect(dateSet.size).toBe(1);
            expect(dateSet.has(new Date(2025, 0, 1))).toBe(true);
        });

        it('supports chaining with add()', () => {
            const dateSet = new DateSet()
                .add(new Date(2025, 0, 1))
                .add(new Date(2025, 0, 2))
                .add(new Date(2025, 0, 3));

            expect(dateSet.size).toBe(3);
        });

        it('deletes a date from the set', () => {
            const dateSet = new DateSet([new Date(2025, 0, 1), new Date(2025, 0, 2)]);
            const wasDeleted = dateSet.delete(new Date(2025, 0, 1));

            expect(wasDeleted).toBe(true);
            expect(dateSet.size).toBe(1);
            expect(dateSet.has(new Date(2025, 0, 1))).toBe(false);
        });

        it('returns false when deleting non-existent date', () => {
            const dateSet = new DateSet([new Date(2025, 0, 1)]);
            const wasDeleted = dateSet.delete(new Date(2025, 0, 2));

            expect(wasDeleted).toBe(false);
            expect(dateSet.size).toBe(1);
        });
    });

    describe('clear()', () => {
        it('removes all dates from the set', () => {
            const dateSet = new DateSet([
                new Date(2025, 0, 1),
                new Date(2025, 0, 2),
                new Date(2025, 0, 3),
            ]);

            dateSet.clear();

            expect(dateSet.size).toBe(0);
        });
    });

    describe('static factories', () => {

        it('creates range with fromRange()', () => {
            const dateSet = DateSet.fromRange(
                new Date(2025, 0, 1),
                new Date(2025, 0, 5)
            );

            expect(dateSet.size).toBe(5);
            expect(dateSet.has(new Date(2025, 0, 1))).toBe(true);
            expect(dateSet.has(new Date(2025, 0, 3))).toBe(true);
            expect(dateSet.has(new Date(2025, 0, 5))).toBe(true);
            expect(dateSet.has(new Date(2025, 0, 6))).toBe(false);
        });

        it('fromRange() works with reversed start/end', () => {
            const dateSet = DateSet.fromRange(
                new Date(2025, 0, 5),
                new Date(2025, 0, 1)
            );

            expect(dateSet.size).toBe(5);
        });

        it('fromRange() excludes specified dates', () => {
            const dateSet = DateSet.fromRange(
                new Date(2025, 0, 1),
                new Date(2025, 0, 5),
                [new Date(2025, 0, 2), new Date(2025, 0, 4)]
            );

            expect(dateSet.size).toBe(3);
            expect(dateSet.has(new Date(2025, 0, 1))).toBe(true);
            expect(dateSet.has(new Date(2025, 0, 2))).toBe(false);
            expect(dateSet.has(new Date(2025, 0, 3))).toBe(true);
            expect(dateSet.has(new Date(2025, 0, 4))).toBe(false);
            expect(dateSet.has(new Date(2025, 0, 5))).toBe(true);
        });

        it('fromRange() with only start date', () => {
            const dateSet = DateSet.fromRange(new Date(2025, 0, 15), undefined);

            expect(dateSet.size).toBe(1);
            expect(dateSet.has(new Date(2025, 0, 15))).toBe(true);
        });

        it('fromRange() with only end date', () => {
            const dateSet = DateSet.fromRange(undefined, new Date(2025, 0, 15));

            expect(dateSet.size).toBe(1);
            expect(dateSet.has(new Date(2025, 0, 15))).toBe(true);
        });

        it('fromRange() with no dates returns empty', () => {
            const dateSet = DateSet.fromRange(undefined, undefined);

            expect(dateSet.size).toBe(0);
        });
    });

    describe('iteration', () => {
        it('iterates over dates in chronological order', () => {
            const dateSet = new DateSet([
                new Date(2025, 0, 3),
                new Date(2025, 0, 1),
                new Date(2025, 0, 2),
            ]);

            const dates = Array.from(dateSet);

            expect(dates).toHaveLength(3);
            expect(dates[0]).toEqual(new Date(2025, 0, 1));
            expect(dates[1]).toEqual(new Date(2025, 0, 2));
            expect(dates[2]).toEqual(new Date(2025, 0, 3));
        });

        it('can be spread into array', () => {
            const dateSet = new DateSet([
                new Date(2025, 0, 1),
                new Date(2025, 0, 2),
            ]);

            const dates = [...dateSet];
            expect(dates).toHaveLength(2);
        });
    });

    describe('min() and max()', () => {
        it('returns earliest date with min()', () => {
            const dateSet = new DateSet([
                new Date(2025, 0, 15),
                new Date(2025, 0, 1),
                new Date(2025, 0, 30),
            ]);

            const min = dateSet.min();
            expect(min).toEqual(new Date(2025, 0, 1));
        });

        it('returns latest date with max()', () => {
            const dateSet = new DateSet([
                new Date(2025, 0, 15),
                new Date(2025, 0, 1),
                new Date(2025, 0, 30),
            ]);

            const max = dateSet.max();
            expect(max).toEqual(new Date(2025, 0, 30));
        });

        it('returns undefined for empty set', () => {
            const dateSet = new DateSet();

            expect(dateSet.min()).toBeUndefined();
            expect(dateSet.max()).toBeUndefined();
        });
    });

    describe('edge cases', () => {
        it('handles dates across month boundaries', () => {
            const dateSet = DateSet.fromRange(
                new Date(2025, 0, 30),
                new Date(2025, 1, 2)
            );

            expect(dateSet.size).toBe(4);
            expect(dateSet.has(new Date(2025, 0, 30))).toBe(true);
            expect(dateSet.has(new Date(2025, 0, 31))).toBe(true);
            expect(dateSet.has(new Date(2025, 1, 1))).toBe(true);
            expect(dateSet.has(new Date(2025, 1, 2))).toBe(true);
        });

        it('handles dates across year boundaries', () => {
            const dateSet = DateSet.fromRange(
                new Date(2024, 11, 30),
                new Date(2025, 0, 2)
            );

            expect(dateSet.size).toBe(4);
            expect(dateSet.has(new Date(2024, 11, 31))).toBe(true);
            expect(dateSet.has(new Date(2025, 0, 1))).toBe(true);
        });

        it('handles leap year dates', () => {
            const dateSet = DateSet.fromRange(
                new Date(2024, 1, 28),
                new Date(2024, 2, 1)
            );

            expect(dateSet.size).toBe(3); // Feb 28, 29, Mar 1
            expect(dateSet.has(new Date(2024, 1, 29))).toBe(true);
        });

        it('handles DST transitions', () => {
            // March 9, 2025: DST starts in US
            const dateSet = DateSet.fromRange(
                new Date(2025, 2, 8),
                new Date(2025, 2, 10)
            );

            expect(dateSet.size).toBe(3);
            expect(dateSet.has(new Date(2025, 2, 9))).toBe(true);
        });
    });
});
