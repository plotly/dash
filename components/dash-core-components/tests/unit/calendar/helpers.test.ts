import {
    dateAsNum,
    dateAsStr,
    isDateInRange,
    numAsDate,
    strAsDate,
    formatDate,
    formatMonth,
    extractFormats,
    getMonthOptions,
    formatYear,
    parseYear,
} from '../../../src/utils/calendar/helpers';

describe('dateAsKey and keyAsDate', () => {
    it('supports arithmetic operations', () => {
        const baseKey = dateAsNum(new Date(2025, 0, 15));

        const nextDay = numAsDate(baseKey + 1);
        expect(nextDay).toEqual(new Date(2025, 0, 16));

        const prevDay = numAsDate(baseKey - 1);
        expect(prevDay).toEqual(new Date(2025, 0, 14));

        const nextWeek = numAsDate(baseKey + 7);
        expect(nextWeek).toEqual(new Date(2025, 0, 22));

        const prevWeek = numAsDate(baseKey - 7);
        expect(prevWeek).toEqual(new Date(2025, 0, 8));
    });

    it('maintains perfect symmetry through multiple round-trips', () => {
        // Test edge cases that might reveal timezone bugs:
        // - DST transitions (spring forward/fall back)
        // - Month/year boundaries
        // - Leap year days
        // - Dates before epoch
        const edgeCaseDates = [
            // DST spring forward in US (March 2025, 2am -> 3am)
            new Date(2025, 2, 8),  // Day before
            new Date(2025, 2, 9),  // Day of spring forward
            new Date(2025, 2, 10), // Day after

            // DST fall back in US (November 2025, 2am -> 1am)
            new Date(2025, 10, 1),  // Day before
            new Date(2025, 10, 2),  // Day of fall back
            new Date(2025, 10, 3),  // Day after

            // Month boundaries
            new Date(2025, 0, 31),  // Jan 31 -> Feb 1
            new Date(2025, 1, 1),   // Feb 1

            // Year boundaries
            new Date(2024, 11, 31), // Dec 31, 2024
            new Date(2025, 0, 1),   // Jan 1, 2025

            // Leap year
            new Date(2024, 1, 28),  // Feb 28 (leap year)
            new Date(2024, 1, 29),  // Feb 29 (leap day)
            new Date(2024, 2, 1),   // Mar 1 after leap day
            new Date(2025, 1, 28),  // Feb 28 (non-leap year)
            new Date(2025, 2, 1),   // Mar 1 (non-leap year)

            // Before epoch
            new Date(1969, 11, 31), // Dec 31, 1969
            new Date(1969, 11, 30), // Dec 30, 1969
            new Date(1969, 0, 1),   // Jan 1, 1969
        ];

        for (const originalDate of edgeCaseDates) {
            // Do multiple round trips to catch any accumulating errors
            const key1 = dateAsNum(originalDate);
            const date1 = numAsDate(key1);
            const key2 = dateAsNum(date1);
            const date2 = numAsDate(key2);
            const key3 = dateAsNum(date2);

            // All keys should be identical
            expect(key1).toBe(key2);
            expect(key2).toBe(key3);

            // All dates should be identical
            expect(date1).toEqual(originalDate);
            expect(date2).toEqual(originalDate);
            expect(date2).toEqual(date1);
        }
    });

    it('dateAsKey supports arithmetic operations on keys', () => {
        const baseDate = new Date(2025, 0, 15); // Jan 15, 2025
        const baseKey = dateAsNum(baseDate);

        const nextDay = dateAsNum(new Date(2025, 0, 16));
        expect(baseKey + 1).toBe(nextDay);

        const prevDay = dateAsNum(new Date(2025, 0, 14));
        expect(baseKey - 1).toBe(prevDay);

        const nextWeek = dateAsNum(new Date(2025, 0, 22));
        expect(baseKey + 7).toBe(nextWeek);

        const prevWeek = dateAsNum(new Date(2025, 0, 8));
        expect(baseKey - 7).toBe(prevWeek);

        const nextMonth = dateAsNum(new Date(2025, 1, 14)); // 30 days later
        expect(baseKey + 30).toBe(nextMonth);

        const prevMonth = dateAsNum(new Date(2024, 11, 16)); // 30 days before
        expect(baseKey - 30).toBe(prevMonth);

        const nextYear = dateAsNum(new Date(2026, 0, 15)); // 365 days in 2025
        expect(baseKey + 365).toBe(nextYear);

        const prevYear = dateAsNum(new Date(2024, 0, 15)); // 366 days in 2024 (leap year)
        expect(baseKey - 366).toBe(prevYear);
    });

    it('handles dates before Unix epoch (negative keys)', () => {
        const date1 = new Date(1969, 11, 31); // Dec 31, 1969 (day before epoch)
        const date2 = new Date(1969, 11, 30); // Dec 30, 1969

        const key1 = dateAsNum(date1);
        const key2 = dateAsNum(date2);

        expect(key1).toBe(-1);
        expect(key2).toBe(-2);
        expect(key1 - 1).toBe(key2);
    });

    it('handles DST transitions correctly', () => {
        // In US, DST typically happens in March (spring forward) and November (fall back)
        // March 9, 2025 -> March 10, 2025 (spring forward at 2am)
        const beforeDST = new Date(2025, 2, 9);
        const afterDST = new Date(2025, 2, 10);

        const key1 = dateAsNum(beforeDST);
        const key2 = dateAsNum(afterDST);

        // Should still be exactly 1 day apart despite DST
        expect(key1 + 1).toBe(key2);
    });

    it('handles leap year edge cases', () => {
        // Feb 28 -> Feb 29 in a leap year
        const feb28 = new Date(2024, 1, 28);
        const feb29 = new Date(2024, 1, 29);
        const mar1 = new Date(2024, 2, 1);

        expect(dateAsNum(feb28) + 1).toBe(dateAsNum(feb29));
        expect(dateAsNum(feb29) + 1).toBe(dateAsNum(mar1));
        expect(dateAsNum(feb28) + 2).toBe(dateAsNum(mar1));
    });

    it('handles BC dates and year 0 boundary', () => {
        // JavaScript Date constructor interprets 0-99 as 1900-1999
        // Must use setFullYear() to create actual year 0 and year 1
        const year1AD = new Date();
        year1AD.setFullYear(1, 0, 1); // Jan 1, 1 AD

        const year0 = new Date();
        year0.setFullYear(0, 11, 31); // Dec 31, 1 BC (year 0 in ISO 8601)

        const year1BC = new Date();
        year1BC.setFullYear(-1, 11, 31); // Dec 31, 2 BC (year -1 in ISO 8601)

        const key1AD = dateAsNum(year1AD);
        const key0 = dateAsNum(year0);
        const key1BC = dateAsNum(year1BC);

        // Should be consecutive days
        expect(key0 + 1).toBe(key1AD);
        expect(key1BC + 366).toBe(key0); // Year 0 (1 BC) is a leap year
    });
});

describe('strAsDate and dateAsStr', () => {
    it('converts between date strings and Date objects as inverse operations', () => {
        // strAsDate converts "YYYY-MM-DD" strings to Date objects
        // dateAsStr converts Date objects to "YYYY-MM-DD" strings
        // Test a variety of dates including edge cases
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
        expect(strAsDate(`${new Date(2025, 0, 1)}`)).toEqual(new Date(2025, 0, 1));

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
        const minDate = new Date(2025, 0, 10, 14, 30, 0);  // Jan 10, 2025 at 2:30 PM
        const maxDate = new Date(2025, 0, 20, 9, 15, 0);   // Jan 20, 2025 at 9:15 AM

        // Within range (time components ignored)
        expect(isDateInRange(new Date(2025, 0, 10, 0, 0, 1), minDate, maxDate)).toBe(true);    // min boundary
        expect(isDateInRange(new Date(2025, 0, 15, 23, 59, 59), minDate, maxDate)).toBe(true); // middle
        expect(isDateInRange(new Date(2025, 0, 20, 23, 59, 59), minDate, maxDate)).toBe(true); // max boundary

        // Outside range
        expect(isDateInRange(new Date(2025, 0, 9), minDate, maxDate)).toBe(false);  // before min
        expect(isDateInRange(new Date(2025, 0, 21), minDate, maxDate)).toBe(false); // after max
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
    const testDate = new Date(1997, 4, 10); // May 10, 1997

    it('formats dates using moment.js format strings', () => {
        expect(formatDate(testDate, 'YYYY-MM-DD')).toBe('1997-05-10');
        expect(formatDate(testDate, 'MM DD YY')).toBe('05 10 97');
        expect(formatDate(testDate, 'M, D, YYYY')).toBe('5, 10, 1997');
        expect(formatDate(testDate)).toBeTruthy(); // default format
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
        expect(extractFormats('MMMM, YYYY')).toEqual({monthFormat: 'MMMM', yearFormat: 'YYYY'});
        expect(extractFormats('MM YY')).toEqual({monthFormat: 'MM', yearFormat: 'YY'});
        expect(extractFormats('M/YYYY')).toEqual({monthFormat: 'M', yearFormat: 'YYYY'});
    });

    it('uses defaults when format not provided or tokens not found', () => {
        expect(extractFormats()).toEqual({monthFormat: 'MMMM', yearFormat: 'YYYY'});
        expect(extractFormats('invalid')).toEqual({monthFormat: 'MMMM', yearFormat: 'YYYY'});
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

    it('parses 2-digit years using moment.js pivot (00-68 → 2000s, 69-99 → 1900s)', () => {
        expect(parseYear('97')).toBe(1997);
        expect(parseYear('23')).toBe(2023);
        expect(parseYear('68')).toBe(2068);
        expect(parseYear('69')).toBe(1969);
        expect(parseYear('00')).toBe(2000);
    });

    it('handles single-digit years', () => {
        expect(parseYear('5')).toBe(2005);
        expect(parseYear('0')).toBe(2000);
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
