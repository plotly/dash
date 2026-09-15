import {
    format,
    parse,
    parseISO,
    isValid,
    startOfDay,
    startOfMonth,
    isSameDay as dateFnsIsSameDay,
    isBefore,
    isAfter,
    isWithinInterval,
    min,
    max,
    addYears,
    addMonths,
    addDays,
    differenceInDays,
} from 'date-fns';
import type {Locale} from 'date-fns';
import {DatePickerSingleProps, DateStepUnit} from '../../types';

const HOURS_PER_DAY = 24;
const MINUTES_PER_HOUR = 60;
const SECONDS_PER_MINUTE = 60;
const MILLISECONDS_PER_SECOND = 1000;
const DAYS_PER_YEAR = 365.25;
const MONTHS_PER_YEAR = 12;
export const MS_PER_DAY =
    HOURS_PER_DAY *
    MINUTES_PER_HOUR *
    SECONDS_PER_MINUTE *
    MILLISECONDS_PER_SECOND;
export const MS_PER_MONTH = (DAYS_PER_YEAR / MONTHS_PER_YEAR) * MS_PER_DAY;
export const MS_PER_YEAR = DAYS_PER_YEAR * MS_PER_DAY;

declare global {
    interface Window {
        dateFns?: {
            locale?: Record<string, Locale>;
        };
    }
}

/**
 * Converts relevant moment.js format tokens to unicode tokens suitable for use
 * in date-fns. This maintains backwards compatibility with our publicly
 * documented format strings while enabling us to use the date-fns library
 * internally.
 */
function convertFormatTokens(momentFormat: string): string {
    return momentFormat
        .replace(/dd/g, 'EEEEEE') // Day of week abbreviation: Mo, Tu, We
        .replace(/Do/g, 'do') // Ordinal day: 1st, 2nd, 3rd
        .replace(/YYYY/g, 'yyyy') // 4-digit year
        .replace(/YY/g, 'yy') // 2-digit year
        .replace(/Y/g, 'y') // Year (numeric, variable length)
        .replace(/DD/g, 'dd') // Day of month with leading zero
        .replace(/D/g, 'd') // Day of month
        .replace(/X/g, 't'); // Unix timestamp (seconds)
}

/**
 * Matches the user's preferred locale against the locales that have been loaded
 * externally on the page from the assets folder or via a script tag
 */
export function getUserLocale(): Locale | undefined {
    // Check if page has loaded any external locales
    const availableLocales = window.dateFns?.locale ?? {};

    // Match available locales against user locale preferences
    const localeKeys = Object.keys(availableLocales);
    const userLanguages = navigator.languages || [navigator.language];
    for (const lang of userLanguages) {
        // First check full locale string for regional variants (e.g., 'fr-CA')
        const normalizedLang = lang.replace('-', '');
        if (availableLocales[normalizedLang]) {
            return availableLocales[normalizedLang];
        }

        // Fallback to simple language code (e.g., 'fr')
        const langCode = lang.split('-')[0];
        if (availableLocales[langCode]) {
            return availableLocales[langCode];
        }
    }

    // No match found against user language preferences, we'll use first
    // loaded locale (ultimately determined by script order in HTML)
    return availableLocales[localeKeys[0]];
}

export function formatDate(date?: Date, formatStr = 'YYYY-MM-DD'): string {
    if (!date) {
        return '';
    }
    const convertedFormat = convertFormatTokens(formatStr);
    return format(date, convertedFormat, {locale: getUserLocale()});
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

export function strAsDate(
    dateStr?: string,
    formatStr?: string
): Date | undefined {
    if (!dateStr) {
        return undefined;
    }

    const locale = getUserLocale();
    let parsed = formatStr
        ? parse(dateStr, convertFormatTokens(formatStr), new Date(), {
              locale,
          })
        : parseISO(dateStr);

    // Fallback to native Date constructor for non-ISO formats
    if (!isValid(parsed)) {
        parsed = new Date(dateStr);
    }

    return isValid(parsed) ? startOfDay(parsed) : undefined;
}

type AnyDayFormat = string | Date | DatePickerSingleProps['date'];
export function isSameDay(day1?: AnyDayFormat, day2?: AnyDayFormat): boolean {
    if (!day1 && !day2) {
        return true; // Both undefined/null - considered the same
    }
    if (!day1 || !day2) {
        return false; // Only one is defined - considered different
    }

    // Convert strings to Dates using strAsDate logic
    const date1 = typeof day1 === 'string' ? strAsDate(day1) : day1;
    const date2 = typeof day2 === 'string' ? strAsDate(day2) : day2;

    // strAsDate returns undefined for invalid dates
    if (!date1 || !date2) {
        return false;
    }

    return dateFnsIsSameDay(date1, date2);
}

export function isDateInRange(
    targetDate: Date,
    minDate?: Date,
    maxDate?: Date
): boolean {
    const target = startOfDay(targetDate);

    // If both dates are provided, normalize them to ensure min <= max
    if (minDate && maxDate) {
        const dates = [startOfDay(minDate), startOfDay(maxDate)];
        return isWithinInterval(target, {
            start: min(dates),
            end: max(dates),
        });
    }

    if (minDate && isBefore(target, startOfDay(minDate))) {
        return false;
    }

    if (maxDate && isAfter(target, startOfDay(maxDate))) {
        return false;
    }

    return true;
}

/**
 * Converts a YYYY-MM-DD date string to milliseconds.
 * Always treats dates as UTC to avoid timezone shifts.
 */
export function dateStringToTimestamp(
    dateStr: string | null | undefined
): number | undefined {
    if (!dateStr) {
        return undefined;
    }
    const [year, month, day] = dateStr.split('-').map(Number);
    return Date.UTC(year, month - 1, day);
}

/**
 * Converts milliseconds since epoch to a YYYY-MM-DD date string.
 * Always treats dates as UTC to avoid timezone shifts.
 */
export function timestampToDateString(
    timestamp: number | undefined
): string | undefined {
    if (timestamp === undefined || timestamp === null) {
        return undefined;
    }
    const days = Math.round(timestamp / MS_PER_DAY);
    return new Date(days * MS_PER_DAY).toISOString().split('T')[0];
}

/**
 * Checks if a date is disabled based on min/max constraints
 */
export function isDateDisabled(
    date: Date,
    minDate?: Date,
    maxDate?: Date,
    disabledDates?: Date[]
): boolean {
    if (!isDateInRange(date, minDate, maxDate)) {
        return true;
    }

    if (disabledDates) {
        return disabledDates.some(d => isSameDay(date, d));
    }

    return false;
}

export function formatMonth(
    year: number,
    month: number,
    formatStr?: string
): string {
    const {monthFormat} = extractFormats(formatStr);
    const convertedFormat = convertFormatTokens(monthFormat);
    return format(new Date(year, month, 1), convertedFormat, {
        locale: getUserLocale(),
    });
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
    formatStr?: string,
    minDate?: Date,
    maxDate?: Date
): Array<{label: string; value: number; disabled?: boolean}> {
    const {monthFormat} = extractFormats(formatStr);
    const convertedFormat = convertFormatTokens(monthFormat);

    return Array.from({length: 12}, (_, i) => {
        const monthStart = new Date(year, i, 1);
        const label = format(monthStart, convertedFormat, {
            locale: getUserLocale(),
        });

        // Check if this month is outside the allowed range (month-level comparison)
        const disabled =
            (minDate && isBefore(monthStart, startOfMonth(minDate))) ||
            (maxDate && isAfter(monthStart, startOfMonth(maxDate)));

        return {label, value: i, disabled};
    });
}

/**
 * Formats a year according to the year format extracted from month_format.
 */
export function formatYear(year: number, formatStr?: string): string {
    const {yearFormat} = extractFormats(formatStr);
    const convertedFormat = convertFormatTokens(yearFormat);
    return format(new Date(year, 0, 1), convertedFormat, {
        locale: getUserLocale(),
    });
}

/**
 * Parses a year string and converts it to a full 4-digit year.
 * Uses date-fns pivot: 2-digit years are interpreted within ±50 years of current year.
 * Example (when current year is 2025): 00-74 → 2000-2074, 75-99 → 1975-1999
 */
export function parseYear(yearStr: string): number | undefined {
    const formats = ['yy', 'yyyy'];
    for (const fmt of formats) {
        const parsed = parse(yearStr.trim(), fmt, new Date());
        if (isValid(parsed)) {
            return parsed.getFullYear();
        }
    }
    return undefined;
}

/**
 * Returns the next date after applying a step with a stepUnit to a start date.
 */
export function stepDate(
    date?: Date,
    step?: number | null,
    stepUnit?: DateStepUnit | null
): Date | undefined {
    if (!date || !step || !stepUnit) {
        return undefined;
    }
    if (stepUnit === 'years') {
        return addYears(date, step);
    }
    if (stepUnit === 'months') {
        return addMonths(date, step);
    }
    return addDays(date, step);
}

/**
 * Snaps a date to the nearest valid step interval relative to an anchor date.
 *
 * Example:
 * anchor = 2025-01-01, step = 7, stepUnit = 'days'
 *
 * Valid snapped dates:
 * 2025-01-01, 2025-01-08, 2025-01-15, ...
 */
export function snapToStep(
    date: Date,
    anchor: Date,
    step: number,
    stepUnit: DateStepUnit
): Date {
    const nthStep = (n: number): Date =>
        stepDate(anchor, step * n, stepUnit) ?? anchor;

    const diffMs = date.getTime() - anchor.getTime();
    const msPerUnit =
        stepUnit === 'years'
            ? MS_PER_YEAR
            : stepUnit === 'months'
            ? MS_PER_MONTH
            : MS_PER_DAY;

    const approxN = Math.floor(diffMs / (step * msPerUnit));

    const candidates = [
        nthStep(approxN - 1),
        nthStep(approxN),
        nthStep(approxN + 1),
    ];

    return candidates.reduce((a, b) =>
        Math.abs(differenceInDays(date, a)) <=
        Math.abs(differenceInDays(date, b))
            ? a
            : b
    );
}
