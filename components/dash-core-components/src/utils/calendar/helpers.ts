import moment from 'moment';
import {DatePickerSingleProps} from '../../types';

export function formatDate(date?: Date, format = 'YYYY-MM-DD'): string {
    if (!date) {
        return '';
    }
    return moment(date).format(format);
}

/*
 * Outputs a date object in YYYY-MM-DD format, suitable for use in props
 */
export function dateAsStr(
    date?: Date
): `${string}-${string}-${string}` | undefined {
    if (!date) {
        return undefined;
    }
    return formatDate(date, 'YYYY-MM-DD') as `${string}-${string}-${string}`;
}

export function strAsDate(date?: string, format?: string): Date | undefined {
    if (!date) {
        return undefined;
    }
    const parsed = format ? moment(date, format, true) : moment(date);
    if (!parsed.isValid()) {
        return undefined;
    }
    return parsed.startOf('day').toDate();
}

type AnyDayFormat = string | Date | DatePickerSingleProps['date'];
export function isSameDay(day1?: AnyDayFormat, day2?: AnyDayFormat): boolean {
    if (!day1 && !day2) {
        return true; // Both undefined/null - considered the same
    }
    if (!day1 || !day2) {
        return false; // Only one is defined - considered different
    }
    return moment(day1).isSame(day2, 'day');
}

export function isDateInRange(
    targetDate: Date,
    minDate?: Date,
    maxDate?: Date
): boolean {
    const target = moment(targetDate);

    // If both dates are provided, normalize them to ensure min <= max
    if (minDate && maxDate) {
        const min = moment(minDate);
        const max = moment(maxDate);
        const [actualMin, actualMax] = min.isSameOrBefore(max, 'day')
            ? [min, max]
            : [max, min];

        return (
            target.isSameOrAfter(actualMin, 'day') &&
            target.isSameOrBefore(actualMax, 'day')
        );
    }

    if (minDate && target.isBefore(moment(minDate), 'day')) {
        return false;
    }

    if (maxDate && target.isAfter(moment(maxDate), 'day')) {
        return false;
    }

    return true;
}

/**
 * Checks if a date is disabled based on min/max constraints and disabled dates array.
 */
export function isDateDisabled(
    date: Date,
    minDate?: Date,
    maxDate?: Date,
    disabledDates?: Date[]
): boolean {
    // Check if date is outside min/max range
    if (!isDateInRange(date, minDate, maxDate)) {
        return true;
    }

    // Check if date is in the disabled dates array
    if (disabledDates) {
        return disabledDates.some(d => isSameDay(date, d));
    }

    return false;
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
 * Extracts separate month and year format strings from a combined month_format, e.g. "MMM YY".
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
 */
export function getMonthOptions(
    year: number,
    format?: string,
    minDate?: Date,
    maxDate?: Date
): Array<{label: string; value: number; disabled?: boolean}> {
    const {monthFormat} = extractFormats(format);

    return Array.from({length: 12}, (_, i) => {
        const monthStart = moment([year, i, 1]);
        const label = monthStart.format(monthFormat);

        // Check if this month is outside the allowed range
        const disabled =
            (minDate && monthStart.isBefore(moment(minDate), 'month')) ||
            (maxDate && monthStart.isAfter(moment(maxDate), 'month'));

        return {label, value: i, disabled};
    });
}

/**
 * Formats a year according to the year format extracted from month_format.
 */
export function formatYear(year: number, format?: string): string {
    const {yearFormat} = extractFormats(format);
    return moment(new Date(year, 0, 1)).format(yearFormat);
}

/**
 * Parses a year string and converts it to a full 4-digit year.
 */
export function parseYear(yearStr: string): number | undefined {
    const parsed = moment(yearStr, ['YY', 'YYYY']);
    return parsed.isValid() ? parsed.year() : undefined;
}
