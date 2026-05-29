import {
    dateAsStr,
    isDateInRange,
    isDateDisabled,
    strAsDate,
    formatDate,
    formatMonth,
    extractFormats,
    getMonthOptions,
    formatYear,
    parseYear,
    stepDate,
    parseDisabledDates,
    expandDisableFlags,
    snapToValidDate,
    snapToStep,
    enforceNoDisabledInBetween,
} from '../../../src/utils/calendar/helpers';

describe('strAsDate and dateAsStr', () => {
    it('converts between date strings and Date objects as inverse operations', () => {
        const testDates = [
            new Date(2025, 0, 15), // Jan 15, 2025 (regular date)
            new Date(2025, 0, 1), // Jan 1 (start of year)
            new Date(2024, 1, 29), // Feb 29, 2024 (leap year)
            new Date(2025, 11, 31), // Dec 31 (end of year)
            new Date(1969, 11, 31), // Dec 31, 1969 (before Unix epoch)
            new Date(1900, 0, 1), // Jan 1, 1900 (far past)
            new Date(2100, 5, 15), // Jun 15, 2100 (far future)
        ];

        for (const date of testDates) {
            const str = dateAsStr(date);
            const roundTrip = strAsDate(str);
            expect(roundTrip).toEqual(date);

            // Verify proper formatting with zero-padding
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            expect(str).toBe(`${year}-${month}-${day}`);
        }
    });

    it('handles undefined and invalid inputs correctly', () => {
        // Strange formatting
        expect(strAsDate('2025-01')).toEqual(new Date(2025, 0, 1));
        expect(strAsDate('2025/01/15')).toEqual(new Date(2025, 0, 15));
        expect(strAsDate('2025-01-15T14:30:45')).toEqual(new Date(2025, 0, 15));
        expect(strAsDate(`${new Date(2025, 0, 1)}`)).toEqual(
            new Date(2025, 0, 1)
        );

        // Undefined values
        expect(dateAsStr(undefined)).toBeUndefined();
        expect(strAsDate(undefined)).toBeUndefined();
        expect(strAsDate('')).toBeUndefined();

        // Invalid formats
        expect(strAsDate('invalid')).toBeUndefined();
    });

    it('accepts Python datetime string representations', () => {
        // Python datetime.datetime objects stringify with time components
        // e.g., datetime(2025, 1, 15, 14, 30, 45, 123456) -> "2025-01-15 14:30:45.123456"

        // With full precision (microseconds)
        const fullPrecision = strAsDate('2025-01-15 14:30:45.123456');
        expect(fullPrecision).toEqual(new Date(2025, 0, 15));

        // With seconds only
        const withSeconds = strAsDate('2025-01-15 14:30:45');
        expect(withSeconds).toEqual(new Date(2025, 0, 15));

        // With minutes only
        const withMinutes = strAsDate('2025-01-15 14:30');
        expect(withMinutes).toEqual(new Date(2025, 0, 15));

        // Edge cases
        const midnight = strAsDate('2025-01-15 00:00:00');
        expect(midnight).toEqual(new Date(2025, 0, 15));

        const endOfDay = strAsDate('2025-01-15 23:59:59.999999');
        expect(endOfDay).toEqual(new Date(2025, 0, 15));
    });
});

describe('isDateInRange', () => {
    it('checks if date is within range (inclusive boundaries, normalized to midnight)', () => {
        const minDate = new Date(2025, 0, 10, 14, 30, 0); // Jan 10, 2025 at 2:30 PM
        const maxDate = new Date(2025, 0, 20, 9, 15, 0); // Jan 20, 2025 at 9:15 AM

        // Within range (time components ignored)
        expect(
            isDateInRange(new Date(2025, 0, 10, 0, 0, 1), minDate, maxDate)
        ).toBe(true); // min boundary
        expect(
            isDateInRange(new Date(2025, 0, 15, 23, 59, 59), minDate, maxDate)
        ).toBe(true); // middle
        expect(
            isDateInRange(new Date(2025, 0, 20, 23, 59, 59), minDate, maxDate)
        ).toBe(true); // max boundary

        // Outside range
        expect(isDateInRange(new Date(2025, 0, 9), minDate, maxDate)).toBe(
            false
        ); // before min
        expect(isDateInRange(new Date(2025, 0, 21), minDate, maxDate)).toBe(
            false
        ); // after max
    });

    it('handles undefined min/max dates (no range restrictions)', () => {
        const someDate = new Date(2025, 5, 15);

        expect(isDateInRange(someDate, undefined, undefined)).toBe(true);

        const minDate = new Date(2025, 0, 1);
        const dateAfterMin = new Date(2025, 5, 15);
        const dateBeforeMin = new Date(2024, 11, 31);

        expect(isDateInRange(dateAfterMin, minDate, undefined)).toBe(true);
        expect(isDateInRange(dateBeforeMin, minDate, undefined)).toBe(false);

        const maxDate = new Date(2025, 11, 31);
        const dateBeforeMax = new Date(2025, 5, 15);
        const dateAfterMax = new Date(2026, 0, 1);

        expect(isDateInRange(dateBeforeMax, undefined, maxDate)).toBe(true);
        expect(isDateInRange(dateAfterMax, undefined, maxDate)).toBe(false);
    });
});

describe('formatDate', () => {
    const testDate = new Date(1997, 4, 10); // May 10, 1997 (Saturday)

    it('formats dates using moment.js format strings', () => {
        expect(formatDate(testDate, 'YYYY-MM-DD')).toBe('1997-05-10');
        expect(formatDate(testDate, 'MM DD YY')).toBe('05 10 97');
        expect(formatDate(testDate, 'M, D, YYYY')).toBe('5, 10, 1997');
        expect(formatDate(testDate)).toBeTruthy(); // default format
    });

    it('handles ordinal day format (Do)', () => {
        const date1st = new Date(2025, 0, 1);
        const date2nd = new Date(2025, 0, 2);
        const date3rd = new Date(2025, 0, 3);
        const date21st = new Date(2025, 0, 21);

        expect(formatDate(date1st, 'MMM Do, YYYY')).toBe('Jan 1st, 2025');
        expect(formatDate(date2nd, 'MMM Do, YYYY')).toBe('Jan 2nd, 2025');
        expect(formatDate(date3rd, 'MMM Do, YYYY')).toBe('Jan 3rd, 2025');
        expect(formatDate(date21st, 'MMM Do, YYYY')).toBe('Jan 21st, 2025');
    });

    it('handles day of week abbreviation (dd)', () => {
        // testDate is Saturday, May 10, 1997
        expect(formatDate(testDate, 'dd, MMM D')).toBe('Sa, May 10');
    });

    it('handles quarter format (Q)', () => {
        const q1 = new Date(2025, 0, 15); // January = Q1
        const q2 = new Date(2025, 4, 15); // May = Q2
        const q3 = new Date(2025, 7, 15); // August = Q3
        const q4 = new Date(2025, 10, 15); // November = Q4

        expect(formatDate(q1, 'Q-YYYY')).toBe('1-2025');
        expect(formatDate(q2, 'Q-YYYY')).toBe('2-2025');
        expect(formatDate(q3, 'Q-YYYY')).toBe('3-2025');
        expect(formatDate(q4, 'Q-YYYY')).toBe('4-2025');
    });

    it('handles Unix timestamp format (X)', () => {
        const testTimestamp = new Date(2025, 0, 1, 0, 0, 0, 0);
        const formatted = formatDate(testTimestamp, 'X');
        // Should be a valid Unix timestamp (seconds since epoch)
        expect(parseInt(formatted, 10)).toBeGreaterThan(1700000000);
    });
});

describe('formatMonth', () => {
    it('extracts and formats only month tokens from combined format strings', () => {
        // Accepts combined month/year formats but only returns month portion
        expect(formatMonth(1997, 4, 'MM YY')).toBe('05');
        expect(formatMonth(1997, 4, 'M/YYYY')).toBe('5');
        expect(formatMonth(1997, 4, 'MMMM, YYYY')).toMatch(/May/);

        // Also works with month-only formats
        expect(formatMonth(1997, 4, 'MMMM')).toMatch(/May/);
        expect(formatMonth(1997, 4, 'MMM')).toMatch(/May/);
    });
});

describe('extractFormats', () => {
    it('extracts month and year format tokens separately', () => {
        expect(extractFormats('MMMM, YYYY')).toEqual({
            monthFormat: 'MMMM',
            yearFormat: 'YYYY',
        });
        expect(extractFormats('MM YY')).toEqual({
            monthFormat: 'MM',
            yearFormat: 'YY',
        });
        expect(extractFormats('M/YYYY')).toEqual({
            monthFormat: 'M',
            yearFormat: 'YYYY',
        });
    });

    it('uses defaults when format not provided or tokens not found', () => {
        expect(extractFormats()).toEqual({
            monthFormat: 'MMMM',
            yearFormat: 'YYYY',
        });
        expect(extractFormats('invalid')).toEqual({
            monthFormat: 'MMMM',
            yearFormat: 'YYYY',
        });
    });
});

describe('getMonthOptions', () => {
    it('generates 12 month options formatted according to month_format', () => {
        const options = getMonthOptions(1997);
        expect(options).toHaveLength(12);
        expect(options[0].value).toBe(0);
        expect(options[11].value).toBe(11);

        // Numeric formats
        expect(getMonthOptions(1997, 'MM')[0].label).toBe('01');
        expect(getMonthOptions(1997, 'M')[0].label).toBe('1');

        // Name formats (use regex due to locale variations)
        expect(getMonthOptions(1997, 'MMMM')[0].label).toMatch(/January/);
        expect(getMonthOptions(1997, 'MMM')[0].label).toMatch(/Jan/);

        // Combined format - extracts only month portion
        const combined = getMonthOptions(1997, 'MMMM, YYYY');
        expect(combined[0].label).toMatch(/January/);
        expect(combined[0].label).not.toMatch(/1997/);
    });
});

describe('formatYear', () => {
    it('formats year as YYYY or YY based on extracted year format', () => {
        // Default YYYY
        expect(formatYear(1997)).toBe('1997');
        expect(formatYear(2023)).toBe('2023');

        // YY format
        expect(formatYear(1997, 'MMMM, YY')).toBe('97');
        expect(formatYear(2023, 'MM YY')).toBe('23');
        expect(formatYear(2005, 'M/YY')).toBe('05');

        // YYYY format
        expect(formatYear(1997, 'MMMM, YYYY')).toBe('1997');
        expect(formatYear(2023, 'MM YYYY')).toBe('2023');
    });
});

describe('parseYear', () => {
    it('parses 4-digit years as-is', () => {
        expect(parseYear('1997')).toBe(1997);
        expect(parseYear('2023')).toBe(2023);
        expect(parseYear('2000')).toBe(2000);
    });

    it('parses 2-digit years using date-fns pivot (based on reference date)', () => {
        expect(parseYear('23')).toBe(2023);
        expect(parseYear('00')).toBe(2000);
        expect(parseYear('99')).toBe(1999);
        // Pivot depends on current year - years close to now are 2000s, far future becomes 1900s
    });

    it('returns undefined for invalid inputs', () => {
        expect(parseYear('')).toBeUndefined();
        expect(parseYear('   ')).toBeUndefined();
        expect(parseYear('abc')).toBeUndefined();
    });

    it('handles whitespace trimming', () => {
        expect(parseYear(' 1997 ')).toBe(1997);
        expect(parseYear('  97  ')).toBe(1997);
    });
});

describe('stepDate', () => {
    const baseDate = new Date(2026, 4, 4); // May 4, 2026

    it('applies years, months, and days together', () => {
        const cases: Array<[string, Date]> = [
            ['1:2:3', new Date(2027, 6, 7)],
            ['0:0:1', new Date(2026, 4, 5)],
            ['1:0:0', new Date(2027, 4, 4)],
            ['0:1:0', new Date(2026, 5, 4)],
        ];

        for (const [step, expected] of cases) {
            expect(stepDate(baseDate, step)).toEqual(expected);
        }
    });

    it('handles zero step components (no-op parts)', () => {
        expect(stepDate(baseDate, '0:0:0')).toEqual(baseDate);
    });

    it('handles month-end overflow correctly', () => {
        const may31 = new Date(2026, 4, 31);
        expect(stepDate(may31, '0:1:0')).toEqual(new Date(2026, 5, 30));
    });

    it('handles leap year transitions', () => {
        const feb29 = new Date(2024, 1, 29);
        expect(stepDate(feb29, '1:0:0')).toEqual(new Date(2025, 1, 28));
    });

    it('returns undefined for missing date or step', () => {
        expect(stepDate(undefined, '1:0:0')).toBeUndefined();
        expect(stepDate(baseDate, undefined)).toBeUndefined();
        expect(stepDate(undefined, undefined)).toBeUndefined();
    });

    it('returns undefined for malformed step strings', () => {
        const invalidSteps = ['1:2', '1:2:3:4', 'a:b:c', '', '1:x:0'];

        for (const step of invalidSteps) {
            expect(stepDate(baseDate, step)).toBeUndefined();
        }
    });
});

describe('isDateDisabled', () => {
    const days = {
        monday: new Date(2026, 4, 4),
        tuesday: new Date(2026, 4, 5),
        wednesday: new Date(2026, 4, 6),
        thursday: new Date(2026, 4, 7),
        friday: new Date(2026, 4, 8),
        saturday: new Date(2026, 4, 9),
        sunday: new Date(2026, 4, 10),
    };

    it('disables dates outside min/max range', () => {
        const min = new Date(2026, 4, 8);
        const max = new Date(2026, 4, 18);
        expect(isDateDisabled(new Date(2026, 4, 5), min, max)).toBe(true);
        expect(isDateDisabled(new Date(2026, 4, 7), min, max)).toBe(true);

        expect(isDateDisabled(new Date(2026, 4, 8), min, max)).toBe(false);
        expect(isDateDisabled(new Date(2026, 4, 10), min, max)).toBe(false);
        expect(isDateDisabled(new Date(2026, 4, 18), min, max)).toBe(false);

        expect(isDateDisabled(new Date(2026, 4, 19), min, max)).toBe(true);
        expect(isDateDisabled(new Date(2026, 4, 21), min, max)).toBe(true);
    });

    it('disables specific dates from array', () => {
        const disabled = [new Date(2026, 4, 15), new Date(2026, 4, 20)];

        expect(
            isDateDisabled(
                new Date(2026, 4, 15),
                undefined,
                undefined,
                disabled
            )
        ).toBe(true);
        expect(
            isDateDisabled(
                new Date(2026, 4, 16),
                undefined,
                undefined,
                disabled
            )
        ).toBe(false);
    });

    it('handles weekend and weekday flags', () => {
        expect(
            isDateDisabled(
                days.saturday,
                undefined,
                undefined,
                undefined,
                undefined,
                'weekends'
            )
        ).toBe(true);
        expect(
            isDateDisabled(
                days.sunday,
                undefined,
                undefined,
                undefined,
                undefined,
                'weekends'
            )
        ).toBe(true);
        expect(
            isDateDisabled(
                days.monday,
                undefined,
                undefined,
                undefined,
                undefined,
                'weekends'
            )
        ).toBe(false);

        expect(
            isDateDisabled(
                days.monday,
                undefined,
                undefined,
                undefined,
                undefined,
                'weekdays'
            )
        ).toBe(true);
        expect(
            isDateDisabled(
                days.saturday,
                undefined,
                undefined,
                undefined,
                undefined,
                'weekdays'
            )
        ).toBe(false);
    });

    it('handles individual day-of-week flags', () => {
        const cases: Array<[string, Date]> = [
            ['mondays', days.monday],
            ['tuesdays', days.tuesday],
            ['wednesdays', days.wednesday],
            ['thursdays', days.thursday],
            ['fridays', days.friday],
            ['saturdays', days.saturday],
            ['sundays', days.sunday],
        ];

        for (const [flag, targetDay] of cases) {
            const otherDay = flag === 'mondays' ? days.tuesday : days.monday;

            expect(
                isDateDisabled(
                    targetDay,
                    undefined,
                    undefined,
                    undefined,
                    undefined,
                    flag as any
                )
            ).toBe(true);
            expect(
                isDateDisabled(
                    otherDay,
                    undefined,
                    undefined,
                    undefined,
                    undefined,
                    flag as any
                )
            ).toBe(false);
        }
    });

    it('handles array of flags', () => {
        const flags = ['mondays', 'wednesdays', 'fridays'] as any;

        expect(
            isDateDisabled(
                days.monday,
                undefined,
                undefined,
                undefined,
                undefined,
                flags
            )
        ).toBe(true);
        expect(
            isDateDisabled(
                days.wednesday,
                undefined,
                undefined,
                undefined,
                undefined,
                flags
            )
        ).toBe(true);
        expect(
            isDateDisabled(
                days.friday,
                undefined,
                undefined,
                undefined,
                undefined,
                flags
            )
        ).toBe(true);
        expect(
            isDateDisabled(
                days.tuesday,
                undefined,
                undefined,
                undefined,
                undefined,
                flags
            )
        ).toBe(false);
    });

    it('combines weekend flag with individual day flag', () => {
        const flags = ['weekends', 'mondays'] as any;

        expect(
            isDateDisabled(
                days.saturday,
                undefined,
                undefined,
                undefined,
                undefined,
                flags
            )
        ).toBe(true);
        expect(
            isDateDisabled(
                days.sunday,
                undefined,
                undefined,
                undefined,
                undefined,
                flags
            )
        ).toBe(true);
        expect(
            isDateDisabled(
                days.monday,
                undefined,
                undefined,
                undefined,
                undefined,
                flags
            )
        ).toBe(true);
        expect(
            isDateDisabled(
                days.tuesday,
                undefined,
                undefined,
                undefined,
                undefined,
                flags
            )
        ).toBe(false);
    });

    it('supports custom predicate function', () => {
        const isThe15th = (d: Date) => d.getDate() === 15;

        expect(
            isDateDisabled(
                new Date(2026, 4, 15),
                undefined,
                undefined,
                undefined,
                undefined,
                isThe15th
            )
        ).toBe(true);
        expect(
            isDateDisabled(
                new Date(2026, 4, 16),
                undefined,
                undefined,
                undefined,
                undefined,
                isThe15th
            )
        ).toBe(false);
    });

    it('combines predicate with flags', () => {
        const isThe15th = (d: Date) => d.getDate() === 15;
        const flags = ['weekends', isThe15th] as any;

        expect(
            isDateDisabled(
                days.saturday,
                undefined,
                undefined,
                undefined,
                undefined,
                flags
            )
        ).toBe(true);
        expect(
            isDateDisabled(
                new Date(2026, 4, 15),
                undefined,
                undefined,
                undefined,
                undefined,
                flags
            )
        ).toBe(true);
        expect(
            isDateDisabled(
                days.monday,
                undefined,
                undefined,
                undefined,
                undefined,
                flags
            )
        ).toBe(false);
    });

    it('returns false when no constraints are set', () => {
        expect(isDateDisabled(days.monday)).toBe(false);
        expect(isDateDisabled(days.sunday)).toBe(false);
    });
});

describe('parseDisabledDates', () => {
    it('returns empty object for undefined input', () => {
        expect(parseDisabledDates(undefined)).toEqual({});
    });

    it('parses individual date strings into Date objects', () => {
        const result = parseDisabledDates(['2026-01-15', '2026-03-20']);
        expect(result.parsedDisabledDates).toHaveLength(2);
        expect(result.parsedDisabledDates![0]).toEqual(new Date(2026, 0, 15));
        expect(result.parsedDisabledDates![1]).toEqual(new Date(2026, 2, 20));
        expect(result.parsedDisabledRanges).toBeUndefined();
    });

    it('parses date range arrays into [Date, Date] tuples', () => {
        const result = parseDisabledDates([['2026-01-01', '2026-01-07']]);
        expect(result.parsedDisabledRanges).toHaveLength(1);
        expect(result.parsedDisabledRanges![0][0]).toEqual(
            new Date(2026, 0, 1)
        );
        expect(result.parsedDisabledRanges![0][1]).toEqual(
            new Date(2026, 0, 7)
        );
        expect(result.parsedDisabledDates).toBeUndefined();
    });

    it('handles mixed individual dates and ranges', () => {
        const result = parseDisabledDates([
            '2026-01-15',
            ['2026-02-01', '2026-02-07'],
            '2026-03-20',
        ]);
        expect(result.parsedDisabledDates).toHaveLength(2);
        expect(result.parsedDisabledRanges).toHaveLength(1);
    });

    it('merges overlapping ranges', () => {
        const result = parseDisabledDates([
            ['2026-01-01', '2026-01-10'],
            ['2026-01-05', '2026-01-15'], // overlaps with previous
        ]);
        expect(result.parsedDisabledRanges).toHaveLength(1);
        expect(result.parsedDisabledRanges![0][0]).toEqual(
            new Date(2026, 0, 1)
        );
        expect(result.parsedDisabledRanges![0][1]).toEqual(
            new Date(2026, 0, 15)
        );
    });

    it('merges adjacent ranges', () => {
        const result = parseDisabledDates([
            ['2026-01-01', '2026-01-10'],
            ['2026-01-10', '2026-01-20'],
        ]);
        expect(result.parsedDisabledRanges).toHaveLength(1);
        expect(result.parsedDisabledRanges![0][1]).toEqual(
            new Date(2026, 0, 20)
        );
    });

    it('keeps non-overlapping ranges separate', () => {
        const result = parseDisabledDates([
            ['2026-01-01', '2026-01-05'],
            ['2026-01-10', '2026-01-15'],
        ]);
        expect(result.parsedDisabledRanges).toHaveLength(2);
    });

    it('merges multiple overlapping ranges correctly', () => {
        const result = parseDisabledDates([
            ['2026-03-01', '2026-03-10'],
            ['2026-01-01', '2026-01-10'],
            ['2026-01-05', '2026-01-20'],
            ['2026-01-15', '2026-01-25'],
        ]);
        expect(result.parsedDisabledRanges).toHaveLength(2);
        expect(result.parsedDisabledRanges![0][0]).toEqual(
            new Date(2026, 0, 1)
        );
        expect(result.parsedDisabledRanges![0][1]).toEqual(
            new Date(2026, 0, 25)
        );
    });

    it('silently ignores invalid date strings', () => {
        const result = parseDisabledDates(['invalid', '2026-01-15']);
        expect(result.parsedDisabledDates).toHaveLength(1);
        expect(result.parsedDisabledDates![0]).toEqual(new Date(2026, 0, 15));
    });

    it('returns undefined arrays when no valid entries of that type exist', () => {
        const result = parseDisabledDates(['2026-01-15']);
        expect(result.parsedDisabledRanges).toBeUndefined();

        const result2 = parseDisabledDates([['2026-01-01', '2026-01-07']]);
        expect(result2.parsedDisabledDates).toBeUndefined();
    });
});

describe('expandDisableFlags', () => {
    const min = new Date(2026, 4, 1); // May 1, 2026 (Friday)
    const max = new Date(2026, 4, 31); // May 31, 2026 (Sunday)

    it('returns empty arrays when no flags match', () => {
        const result = expandDisableFlags([], min, max);
        expect(result.dates).toHaveLength(0);
        expect(result.ranges).toHaveLength(0);
    });

    it('expands weekends into ranges of two days', () => {
        const result = expandDisableFlags('weekends', min, max);
        // All ranges should be Saturday-Sunday pairs
        result.ranges.forEach(([start, end]) => {
            expect(start.getDay()).toBe(6); // Saturday
            expect(end.getDay()).toBe(0); // Sunday
        });
        expect(result.dates).toHaveLength(0);
    });

    it('expands weekdays into ranges of five days', () => {
        const result = expandDisableFlags('weekdays', min, max);
        result.ranges.forEach(([start, end]) => {
            expect(start.getDay()).toBe(1); // Monday
            expect(end.getDay()).toBe(5); // Friday
        });
        // May 1 (Friday) is an isolated weekday at the boundary
        expect(result.dates).toHaveLength(1);
    });

    it('expands a single day flag into individual dates', () => {
        const result = expandDisableFlags('mondays', min, max);
        expect(result.ranges).toHaveLength(0);
        result.dates.forEach(date => {
            expect(date.getDay()).toBe(1); // Monday
        });
        // May 2026 has 4 Mondays (4, 11, 18, 25)
        expect(result.dates).toHaveLength(4);
    });

    it('expands tuesdays correctly', () => {
        const result = expandDisableFlags('tuesdays', min, max);
        result.dates.forEach(date => expect(date.getDay()).toBe(2));
        // May 2026 has 5 Tuesdays (5, 12, 19, 26) - wait, also May 5
        expect(result.dates).toHaveLength(4);
    });

    it('handles array of individual day flags producing separate dates', () => {
        const result = expandDisableFlags(['mondays', 'fridays'], min, max);
        result.dates.forEach(date => {
            expect([1, 5]).toContain(date.getDay());
        });
        expect(result.dates.length).toBeGreaterThan(0);
    });

    it('groups consecutive flags into ranges', () => {
        const result = expandDisableFlags(['mondays', 'tuesdays'], min, max);
        // Mon+Tue should be grouped into ranges, not individual dates
        expect(result.ranges.length).toBeGreaterThan(0);
        result.ranges.forEach(([start, end]) => {
            expect(start.getDay()).toBe(1); // Monday
            expect(end.getDay()).toBe(2); // Tuesday
        });
    });

    it('clamps ranges to min/max bounds', () => {
        const tightMin = new Date(2026, 4, 3); // Sunday
        const tightMax = new Date(2026, 4, 3); // Sunday only
        const result = expandDisableFlags('weekends', tightMin, tightMax);
        result.ranges.forEach(([start, end]) => {
            expect(start.getTime()).toBeGreaterThanOrEqual(tightMin.getTime());
            expect(end.getTime()).toBeLessThanOrEqual(tightMax.getTime());
        });
        result.dates.forEach(date => {
            expect(date.getTime()).toBeGreaterThanOrEqual(tightMin.getTime());
            expect(date.getTime()).toBeLessThanOrEqual(tightMax.getTime());
        });
    });

    it('supports custom predicate function', () => {
        const isThe15th = (d: Date) => d.getDate() === 15;
        const result = expandDisableFlags(isThe15th, min, max);
        expect(result.dates).toHaveLength(1);
        expect(result.dates[0]).toEqual(new Date(2026, 4, 15));
        expect(result.ranges).toHaveLength(0);
    });

    it('all generated dates are within min/max', () => {
        const result = expandDisableFlags('weekends', min, max);
        const allDates = [
            ...result.dates,
            ...result.ranges.flatMap(([s, e]) => [s, e]),
        ];
        allDates.forEach(date => {
            expect(date.getTime()).toBeGreaterThanOrEqual(min.getTime());
            expect(date.getTime()).toBeLessThanOrEqual(max.getTime());
        });
    });
});

describe('snapToValidDate', () => {
    it('returns the same date if it is not disabled', () => {
        const date = new Date(2026, 4, 15);
        expect(snapToValidDate(date)).toEqual(date);
    });

    it('snaps forward when date is inside a disabled range closer to end', () => {
        const date = new Date(2026, 0, 8);
        const ranges: [Date, Date][] = [
            [new Date(2026, 0, 1), new Date(2026, 0, 10)],
        ];
        const result = snapToValidDate(
            date,
            undefined,
            undefined,
            undefined,
            undefined,
            ranges
        );
        expect(result).toEqual(new Date(2026, 0, 11));
    });

    it('snaps to nearest boundary of containing range (closer to start)', () => {
        const date = new Date(2026, 0, 2);
        const ranges: [Date, Date][] = [
            [new Date(2026, 0, 1), new Date(2026, 0, 20)],
        ];
        const result = snapToValidDate(
            date,
            undefined,
            undefined,
            undefined,
            undefined,
            ranges
        );
        expect(result).toEqual(new Date(2025, 11, 31));
    });

    it('snaps to end of range when date is closer to end', () => {
        const date = new Date(2026, 0, 18);
        const ranges: [Date, Date][] = [
            [new Date(2026, 0, 1), new Date(2026, 0, 20)],
        ];
        const result = snapToValidDate(
            date,
            undefined,
            undefined,
            undefined,
            undefined,
            ranges
        );
        expect(result).toEqual(new Date(2026, 0, 21));
    });

    it('snaps away from individually disabled dates', () => {
        const date = new Date(2026, 0, 15);
        const disabled = [new Date(2026, 0, 15)];
        const result = snapToValidDate(
            date,
            undefined,
            undefined,
            undefined,
            disabled
        );
        expect(result).not.toEqual(date);
    });

    it('snaps away from disabled flags', () => {
        const saturday = new Date(2026, 4, 9);
        const result = snapToValidDate(
            saturday,
            undefined,
            undefined,
            undefined,
            undefined,
            undefined,
            'weekends'
        );
        expect([0, 6]).not.toContain(result.getDay());
    });

    it('respects min/max bounds when snapping', () => {
        const date = new Date(2026, 0, 5);
        const minDate = new Date(2026, 0, 1);
        const maxDate = new Date(2026, 0, 10);
        const disabled = [
            new Date(2026, 0, 5),
            new Date(2026, 0, 6),
            new Date(2026, 0, 7),
        ];
        const result = snapToValidDate(
            date,
            undefined,
            minDate,
            maxDate,
            disabled
        );
        expect(result.getTime()).toBeGreaterThanOrEqual(minDate.getTime());
        expect(result.getTime()).toBeLessThanOrEqual(maxDate.getTime());
    });

    it('handles adjacent disabled ranges correctly', () => {
        const date = new Date(2026, 0, 12);
        const ranges: [Date, Date][] = [
            [new Date(2026, 0, 1), new Date(2026, 0, 10)],
            [new Date(2026, 0, 15), new Date(2026, 0, 20)],
        ];
        const result = snapToValidDate(
            date,
            undefined,
            undefined,
            undefined,
            undefined,
            ranges
        );
        expect(result).toEqual(date);
    });

    it('returns original date if no valid date found within bounds', () => {
        const date = new Date(2026, 0, 5);
        const minDate = new Date(2026, 0, 1);
        const maxDate = new Date(2026, 0, 10);
        const ranges: [Date, Date][] = [
            [new Date(2026, 0, 1), new Date(2026, 0, 10)],
        ];
        const result = snapToValidDate(
            date,
            undefined,
            minDate,
            maxDate,
            undefined,
            ranges
        );
        expect(result).toEqual(date);
    });

    it('snaps to step grid when inside disabled range', () => {
        const date = new Date(2026, 0, 8); // inside range
        const ranges: [Date, Date][] = [
            [new Date(2026, 0, 5), new Date(2026, 0, 10)],
        ];
        const result = snapToValidDate(
            date,
            '0:0:3',
            undefined,
            undefined,
            undefined,
            ranges
        );
        expect(result).toEqual(new Date(2026, 0, 11));
    });

    it('walks backward through step grid when after boundary is out of bounds', () => {
        const date = new Date(2026, 0, 8);
        const maxDate = new Date(2026, 0, 10);
        const ranges: [Date, Date][] = [
            [new Date(2026, 0, 5), new Date(2026, 0, 10)],
        ];
        const result = snapToValidDate(
            date,
            '0:0:3',
            undefined,
            maxDate,
            undefined,
            ranges
        );
        expect(result).toEqual(new Date(2026, 0, 2));
    });
});

describe('snapToStep', () => {
    const anchor = new Date(2026, 0, 1); // Jan 1, 2026

    it('returns same date if already on a step boundary', () => {
        expect(snapToStep(anchor, anchor, '0:1:0')).toEqual(anchor);
        expect(snapToStep(new Date(2026, 1, 1), anchor, '0:1:0')).toEqual(
            new Date(2026, 1, 1)
        );
    });

    it('snaps to nearest monthly step', () => {
        // Jan 20 — closer to Feb 1 than Jan 1
        const date = new Date(2026, 0, 20);
        expect(snapToStep(date, anchor, '0:1:0')).toEqual(new Date(2026, 1, 1));

        // Jan 10 — closer to Jan 1 than Feb 1
        const date2 = new Date(2026, 0, 10);
        expect(snapToStep(date2, anchor, '0:1:0')).toEqual(
            new Date(2026, 0, 1)
        );
    });

    it('snaps to nearest weekly step', () => {
        // Jan 1 + 3 days — closer to Jan 1 than Jan 8
        const date = new Date(2026, 0, 4);
        expect(snapToStep(date, anchor, '0:0:7')).toEqual(new Date(2026, 0, 1));

        // Jan 1 + 5 days — closer to Jan 8 than Jan 1
        const date2 = new Date(2026, 0, 6);
        expect(snapToStep(date2, anchor, '0:0:7')).toEqual(
            new Date(2026, 0, 8)
        );
    });

    it('snaps to nearest yearly step', () => {
        const date = new Date(2026, 8, 1); // Sep 2026 — closer to Jan 2027
        expect(snapToStep(date, anchor, '1:0:0')).toEqual(new Date(2027, 0, 1));

        const date2 = new Date(2026, 2, 1); // Mar 2026 — closer to Jan 2026
        expect(snapToStep(date2, anchor, '1:0:0')).toEqual(
            new Date(2026, 0, 1)
        );
    });

    it('handles dates before anchor', () => {
        const date = new Date(2025, 10, 1); // Nov 2025 — before anchor Jan 2026
        const result = snapToStep(date, anchor, '0:1:0');
        // Should snap to nearest month boundary before anchor
        expect(result.getDate()).toBe(1);
        expect(result.getTime()).toBeLessThan(anchor.getTime());
    });

    it('returns date unchanged for empty step string', () => {
        const date = new Date(2026, 0, 15);
        expect(snapToStep(date, anchor, '')).toEqual(date);
    });

    it('snaps correctly with daily step', () => {
        const date = new Date(2026, 0, 5);
        // With step of 1 day, every date is on the grid
        expect(snapToStep(date, anchor, '0:0:1')).toEqual(date);
    });
});

describe('enforceNoDisabledInBetween', () => {
    it('returns newDates unchanged when neither side changed', () => {
        const result = enforceNoDisabledInBetween(
            ['2026-05-01', '2026-05-31'],
            ['2026-05-01', '2026-05-31']
        );
        expect(result).toEqual(['2026-05-01', '2026-05-31']);
    });

    it('collapses to point when new left is disabled', () => {
        const result = enforceNoDisabledInBetween(
            ['2026-05-10', '2026-05-20'],
            ['2026-05-15', '2026-05-20'],
            undefined,
            undefined,
            [new Date(2026, 4, 10)]
        );
        expect(result).toEqual(['2026-05-10', '2026-05-10']);
    });

    it('collapses to point when new right is disabled', () => {
        const result = enforceNoDisabledInBetween(
            ['2026-05-01', '2026-05-20'],
            ['2026-05-01', '2026-05-15'],
            undefined,
            undefined,
            [new Date(2026, 4, 20)]
        );
        expect(result).toEqual(['2026-05-20', '2026-05-20']);
    });

    it('clamps right when expanding left crosses a disabled date', () => {
        const result = enforceNoDisabledInBetween(
            ['2026-05-01', '2026-05-20'],
            ['2026-05-10', '2026-05-20'],
            undefined,
            undefined,
            [new Date(2026, 4, 5)]
        );
        // Right should be clamped to just before May 5
        const [left, right] = result;
        expect(left).toBe('2026-05-01');
        expect(new Date(right).getTime()).toBeLessThan(
            new Date(2026, 4, 5).getTime()
        );
    });

    it('clamps left when expanding right crosses a disabled date', () => {
        const result = enforceNoDisabledInBetween(
            ['2026-05-01', '2026-05-20'],
            ['2026-05-01', '2026-05-10'],
            undefined,
            undefined,
            [new Date(2026, 4, 15)]
        );
        const [left, right] = result;
        expect(right).toBe('2026-05-20');
        expect(new Date(left).getTime()).toBeGreaterThan(
            new Date(2026, 4, 15).getTime()
        );
    });

    it('clamps right when expanding left crosses a disabled range', () => {
        const result = enforceNoDisabledInBetween(
            ['2026-05-01', '2026-05-20'],
            ['2026-05-10', '2026-05-20'],
            undefined,
            undefined,
            undefined,
            [[new Date(2026, 4, 5), new Date(2026, 4, 7)]]
        );
        const [left, right] = result;
        expect(left).toBe('2026-05-01');
        expect(new Date(right).getTime()).toBeLessThan(
            new Date(2026, 4, 5).getTime()
        );
    });

    it('clamps right when expanding left crosses a weekend flag', () => {
        // Expanding left from May 12 to May 4 (Monday), with weekends disabled
        // May 9-10 are Sat-Sun, so right should clamp before May 9
        const result = enforceNoDisabledInBetween(
            ['2026-05-04', '2026-05-20'],
            ['2026-05-12', '2026-05-20'],
            undefined,
            undefined,
            undefined,
            undefined,
            'weekends'
        );
        const [left, right] = result;
        expect(left).toBe('2026-05-04');
        expect(new Date(right).getTime()).toBeLessThan(
            new Date(2026, 4, 9).getTime()
        );
    });

    it('clamps left when expanding right crosses a weekend flag', () => {
        // Expanding right from May 12 to May 20, with weekends disabled
        // May 16-17 are Sat-Sun, so left should clamp after May 17
        const result = enforceNoDisabledInBetween(
            ['2026-05-04', '2026-05-20'],
            ['2026-05-04', '2026-05-12'],
            undefined,
            undefined,
            undefined,
            undefined,
            'weekends'
        );
        const [left, right] = result;
        expect(right).toBe('2026-05-20');
        expect(new Date(left).getTime()).toBeGreaterThan(
            new Date(2026, 4, 17).getTime()
        );
    });

    it('returns newDates unchanged when no disabled dates in between', () => {
        const result = enforceNoDisabledInBetween(
            ['2026-05-01', '2026-05-10'],
            ['2026-05-05', '2026-05-10'],
            undefined,
            undefined,
            [new Date(2026, 4, 20)] // disabled date outside range
        );
        expect(result).toEqual(['2026-05-01', '2026-05-10']);
    });

    it('handles invalid date strings gracefully', () => {
        const result = enforceNoDisabledInBetween(
            ['invalid', '2026-05-20'],
            ['2026-05-01', '2026-05-20']
        );
        expect(result).toEqual(['invalid', '2026-05-20']);
    });

    it('respects min/max when checking if new boundary is disabled', () => {
        const result = enforceNoDisabledInBetween(
            ['2026-04-25', '2026-05-20'],
            ['2026-05-01', '2026-05-20'],
            new Date(2026, 4, 1), // min = May 1
            new Date(2026, 4, 31)
        );
        // Apr 25 is before min, so it's disabled — should collapse
        expect(result).toEqual(['2026-04-25', '2026-04-25']);
    });
});
