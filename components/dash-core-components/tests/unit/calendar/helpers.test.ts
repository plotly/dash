import {
    dateAsStr,
    isDateInRange,
    strAsDate,
    formatDate,
    formatMonth,
    extractFormats,
    getMonthOptions,
    formatYear,
    parseYear,
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
