import {createMonthGrid} from '../../../src/utils/calendar/createMonthGrid';

/**
 * Helper to verify that dates are consecutive
 * Once null padding starts, all subsequent values are null.
 */
const expectConsecutiveDatesUntilPadding = (dates: (Date | null)[]) => {
    let foundFirstNull = false;

    for (let i = 0; i < dates.length; i++) {
        const date = dates[i];

        if (date === null) {
            foundFirstNull = true;
        } else if (foundFirstNull) {
            // Once we hit a single padding cell, all subsequent days should be empty "padding" cells
            fail('Found non-null date after null padding');
        } else if (i > 0 && dates[i - 1] !== null) {
            // Verify consecutive days before padding
            const dayDiff =
                (date.getTime() - dates[i - 1]!.getTime()) /
                (1000 * 60 * 60 * 24);
            expect(dayDiff).toBe(1);
        }
    }
};

describe('createMonthGrid', () => {
    describe('with showOutsideDays=true (default)', () => {
        it('creates grid with exactly 6 rows and 7 columns', () => {
            const grid = createMonthGrid(2025, 0, 0, true);

            expect(grid.length).toBe(6);
            grid.forEach(week => {
                expect(week.length).toBe(7);
            });
        });

        it('has consecutive dates until padding, then all null', () => {
            const grid = createMonthGrid(2025, 0, 0, true);
            expectConsecutiveDatesUntilPadding(grid.flat());
        });

        it('adjusts for different first day of week', () => {
            const sundayFirst = createMonthGrid(2025, 0, 0, true);
            const mondayFirst = createMonthGrid(2025, 0, 1, true);

            expect(sundayFirst[0][0]).not.toBeNull();
            expect(mondayFirst[0][0]).not.toBeNull();
            expect(sundayFirst[0][0]).not.toEqual(mondayFirst[0][0]);

            // January 2025 starts on Wednesday
            // Sunday-first shows 3 days from prev month, Monday-first shows 2
            expect(mondayFirst[0][0]!.getTime()).toBeGreaterThan(
                sundayFirst[0][0]!.getTime()
            );
        });

        it('handles months starting on different weekdays', () => {
            const jan2025 = createMonthGrid(2025, 0, 0, true); // Jan starts on Wednesday
            const feb2025 = createMonthGrid(2025, 1, 0, true); // Feb starts on Saturday

            expect(jan2025.length).toBe(6);
            expect(feb2025.length).toBe(6);
        });

        it('handles February in leap and non-leap years', () => {
            const feb2024 = createMonthGrid(2024, 1, 0, true); // Leap year
            const feb2025 = createMonthGrid(2025, 1, 0, true); // Non-leap year

            // Both should always have exactly 6 rows
            expect(feb2024.length).toBe(6);
            expect(feb2025.length).toBe(6);

            // Verify consecutive dates until padding, then all null
            expectConsecutiveDatesUntilPadding(feb2024.flat());
            expectConsecutiveDatesUntilPadding(feb2025.flat());
        });

        it('creates dates at midnight in local timezone', () => {
            const grid = createMonthGrid(2025, 0, 0, true);
            const firstDate = grid[0][0];

            expect(firstDate).not.toBeNull();
            expect(firstDate!.getHours()).toBe(0);
            expect(firstDate!.getMinutes()).toBe(0);
            expect(firstDate!.getSeconds()).toBe(0);
            expect(firstDate!.getMilliseconds()).toBe(0);
        });

        it('includes correct dates for January 2025', () => {
            const grid = createMonthGrid(2025, 0, 0, true); // January 2025, Sunday first
            const allDates = grid.flat();

            // January 1, 2025 is a Wednesday
            // So grid starts on Sunday, December 29, 2024
            expect(allDates[0]).toEqual(new Date(2024, 11, 29));

            // Find January 1 (should be 4th cell: Sun, Mon, Tue, Wed)
            expect(allDates[3]).toEqual(new Date(2025, 0, 1));

            // Find January 31
            const jan31Index = allDates.findIndex(
                d => d !== null && d.getMonth() === 0 && d.getDate() === 31
            );
            expect(allDates[jan31Index]).toEqual(new Date(2025, 0, 31));
        });
    });

    describe('with showOutsideDays=false', () => {
        it('creates grid with exactly 6 rows and 7 columns', () => {
            const grid = createMonthGrid(2025, 0, 0, false); // January 2025, Sunday first

            // Should always have exactly 6 rows (weeks) for consistent calendar height
            expect(grid.length).toBe(6);

            grid.forEach(week => {
                expect(week.length).toBe(7);
            });
        });

        it('returns null for dates outside the current month', () => {
            const grid = createMonthGrid(2025, 0, 0, false); // January 2025, Sunday first
            const allDates = grid.flat();

            // January 1, 2025 is a Wednesday (4th day of week when Sunday=0)
            // So first 3 cells should be null
            expect(allDates[0]).toBeNull();
            expect(allDates[1]).toBeNull();
            expect(allDates[2]).toBeNull();

            // 4th cell should be January 1
            expect(allDates[3]).toEqual(new Date(2025, 0, 1));

            // Last day of January is the 31st (Friday)
            // Find where January 31 is
            const jan31Index = allDates.findIndex(
                d => d !== null && d.getMonth() === 0 && d.getDate() === 31
            );
            expect(allDates[jan31Index]).toEqual(new Date(2025, 0, 31));

            // Days after January 31 in the same week should be null
            for (let i = jan31Index + 1; i < allDates.length; i++) {
                const d = allDates[i];
                if (d === null) {
                    // null is expected for outside days
                    expect(d).toBeNull();
                } else {
                    // If not null, it should be from a different month
                    expect(d.getMonth()).not.toBe(0);
                }
            }
        });

        it('only includes dates from the current month', () => {
            const grid = createMonthGrid(2025, 0, 0, false); // January 2025
            const allDates = grid.flat();
            const nonNullDates = allDates.filter(d => d !== null) as Date[];

            // All non-null dates should be in January (month 0)
            nonNullDates.forEach(date => {
                expect(date.getMonth()).toBe(0);
            });

            // Should have exactly 31 non-null dates (days in January)
            expect(nonNullDates.length).toBe(31);

            // They should be numbered 1-31
            const dayNumbers = nonNullDates
                .map(d => d.getDate())
                .sort((a, b) => a - b);
            expect(dayNumbers).toEqual(
                Array.from({length: 31}, (_, i) => i + 1)
            );
        });
    });
});
