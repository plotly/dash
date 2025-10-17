import moment from 'moment';

/**
 * Converts a date to a numeric key (days since Unix epoch) for use in Sets/Objects.
 * Normalizes to midnight for consistent comparison.
 * This allows arithmetic operations: key + 1 = next day, key - 7 = previous week
 */
export function dateAsNum(date: Date): number {
    const normalized = new Date(date);
    normalized.setHours(0, 0, 0, 0);
    // eslint-disable-next-line no-magic-numbers
    return Math.floor(normalized.getTime() / (1000 * 60 * 60 * 24));
}

/**
 * Converts a number of days since Unix epoch back into a Date object.
 * Inverse of dateAsNum. Always returns midnight (00:00:00) in local timezone.
 */
export function numAsDate(key: number): Date {
    // Convert key to milliseconds (UTC timestamp)
    // eslint-disable-next-line no-magic-numbers
    const utcDate = new Date(key * 24 * 60 * 60 * 1000);
    // Extract UTC date components and create local date
    return new Date(
        utcDate.getUTCFullYear(),
        utcDate.getUTCMonth(),
        utcDate.getUTCDate()
    );
}

export function strAsDate(date?: string, format?: string): Date | undefined {
    if (!date) {
        return undefined;
    }
    const parsed = format ? moment(date, format, true) : moment(date);
    if (!parsed.isValid()) {
        return undefined;
    }
    // Normalize to midnight in local timezone (strip time component)
    return new Date(parsed.year(), parsed.month(), parsed.date());
}

export function dateAsStr(
    date?: Date
): `${string}-${string}-${string}` | undefined {
    if (!date) {
        return undefined;
    }
    return formatDate(date, 'YYYY-MM-DD') as `${string}-${string}-${string}`;
}

export function isDateInRange(
    targetDate: Date,
    minDate?: Date,
    maxDate?: Date
): boolean {
    const targetKey = dateAsNum(targetDate);

    if (minDate && targetKey < dateAsNum(minDate)) {
        return false;
    }

    if (maxDate && targetKey > dateAsNum(maxDate)) {
        return false;
    }

    return true;
}

export function formatDate(date: Date, format = 'YYYY-MM-DD'): string {
    return moment(date).format(format);
}

export function formatMonth(
    year: number,
    month: number,
    format?: string
): string {
    const {monthFormat} = extractFormats(format);
    return moment(new Date(year, month, 1)).format(monthFormat);
}

/**
 * Extracts separate month and year format strings from a combined month_format.
 * Used when month and year are displayed in separate controls.
 *
 * @param format - The combined format string (e.g., "MMMM, YYYY")
 * @returns Object with monthFormat and yearFormat
 */
export function extractFormats(format?: string): {
    monthFormat: string;
    yearFormat: string;
} {
    if (!format) {
        return {monthFormat: 'MMMM', yearFormat: 'YYYY'};
    }

    // Extract month tokens (MMMM, MMM, MM, M)
    const monthMatch = format.match(/M{1,4}/);
    const monthFormat = monthMatch ? monthMatch[0] : 'MMMM';

    // Extract year tokens (YYYY, YY)
    const yearMatch = format.match(/Y{2,4}/);
    const yearFormat = yearMatch ? yearMatch[0] : 'YYYY';

    return {monthFormat, yearFormat};
}

/**
 * Generates month options for a dropdown based on a format string.
 * Extracts only the month portion from the format and generates all 12 months.
 *
 * @param year - The current year (used for formatting context)
 * @param format - The combined month/year format (e.g., "MMMM, YYYY")
 * @returns Array of {label, value} options for months 0-11
 */
export function getMonthOptions(
    year: number,
    format?: string,
    minDate?: Date,
    maxDate?: Date
): Array<{label: string; value: number; disabled?: boolean}> {
    const {monthFormat} = extractFormats(format);

    return Array.from({length: 12}, (_, i) => {
        const date = new Date(year, i, 1);
        const label = moment(date).format(monthFormat);

        // Check if this month is outside the allowed range
        const disabled =
            (minDate &&
                moment(date).isBefore(moment(minDate).startOf('month'))) ||
            (maxDate && moment(date).isAfter(moment(maxDate).startOf('month')));

        return {label, value: i, disabled};
    });
}

/**
 * Formats a year according to the year format extracted from month_format.
 * Supports YYYY (4-digit) and YY (2-digit) formats.
 *
 * @param year - The full 4-digit year (e.g., 1997)
 * @param format - The combined month/year format (e.g., "MMMM, YY")
 * @returns Formatted year string (e.g., "97" for YY, "1997" for YYYY)
 */
export function formatYear(year: number, format?: string): string {
    const {yearFormat} = extractFormats(format);
    return moment(new Date(year, 0, 1)).format(yearFormat);
}

/**
 * Parses a year string and converts it to a full 4-digit year.
 * Handles both 2-digit (YY) and 4-digit (YYYY) inputs.
 * For 2-digit years, uses moment.js rules: 00-68 → 2000-2068, 69-99 → 1969-1999
 *
 * @param yearStr - The year string to parse (e.g., "97", "1997", "23")
 * @returns Full 4-digit year, or undefined if invalid
 */
export function parseYear(yearStr: string): number | undefined {
    const parsed = moment(yearStr, ['YY', 'YYYY']);
    return parsed.isValid() ? parsed.year() : undefined;
}

/**
 * Checks if a date is disabled based on min/max constraints and disabled dates set.
 *
 * @param date - The date to check
 * @param minDate - Minimum allowed date (optional)
 * @param maxDate - Maximum allowed date (optional)
 * @param disabledDates - DateSet of disabled dates (optional)
 * @returns true if the date is disabled, false otherwise
 */
export function isDateDisabled(
    date: Date,
    minDate?: Date,
    maxDate?: Date,
    disabledDates?: {has: (date: Date) => boolean}
): boolean {
    // Check if date is outside min/max range
    if (!isDateInRange(date, minDate, maxDate)) {
        return true;
    }

    // Check if date is in the disabled dates set (O(1) lookup)
    if (disabledDates) {
        return disabledDates.has(date);
    }

    return false;
}
