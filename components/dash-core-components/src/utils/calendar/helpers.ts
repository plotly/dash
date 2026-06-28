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
    isWeekend,
    min,
    max,
    addYears,
    addMonths,
    addDays,
    getDay,
    differenceInDays,
} from 'date-fns';
import type {Locale} from 'date-fns';
import {
    DatePickerSingleProps,
    DateStepUnit,
    DisableDatesFlag,
    DateSliderMarks,
} from '../../types';

// Conversão para timestamps, deixei global depois posso trocar
// Tenho de separar por causa do lint check
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

export type DisablePredicate = (date: Date) => boolean;

const DAY_FLAGS: Partial<Record<DisableDatesFlag, number>> = {
    sundays: 0,
    mondays: 1,
    tuesdays: 2,
    wednesdays: 3,
    thursdays: 4,
    fridays: 5,
    saturdays: 6,
};

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
 * Checks if a date is disabled based on min/max constraints, disabled dates array,
 * and optional disable flags or custom predicates.
 */
export function isDateDisabled(
    date: Date,
    minDate?: Date,
    maxDate?: Date,
    disabledDates?: Date[],
    disabledRanges?: [Date, Date][],
    disableFlags?:
        | DisableDatesFlag
        | DisablePredicate
        | Array<DisableDatesFlag | DisablePredicate>
): boolean {
    // Check if date is outside min/max range
    if (!isDateInRange(date, minDate, maxDate)) {
        return true;
    }

    // Check if date is in the disabled dates array
    if (disabledDates?.some(d => isSameDay(date, d))) {
        return true;
    }

    // Check if date is in a disabled range
    if (
        disabledRanges?.some(([start, end]) => isDateInRange(date, start, end))
    ) {
        return true;
    }

    // Check if date matches a given flag/predicate
    if (disableFlags) {
        const flags = Array.isArray(disableFlags)
            ? disableFlags
            : [disableFlags];
        return flags.some(flag => {
            if (typeof flag === 'function') {
                return flag(date);
            }
            switch (flag) {
                case 'weekends':
                    return isWeekend(date);
                case 'weekdays':
                    return !isWeekend(date);
                default:
                    return getDay(date) === (DAY_FLAGS[flag] ?? -1);
            }
        });
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
 * Merges overlapping date ranges into a minimal set of non-overlapping ranges.
 * Assumes ranges are inclusive.
 * Example: [[1 Jan, 5 Jan], [3 Jan, 10 Jan]] becomes [[1 Jan, 10 Jan]]
 */
function mergeRanges(ranges: [Date, Date][]): [Date, Date][] {
    if (ranges.length === 0) {
        return [];
    }

    const sorted = [...ranges].sort((a, b) => a[0].getTime() - b[0].getTime());
    const merged: [Date, Date][] = [sorted[0]];

    for (let i = 1; i < sorted.length; i++) {
        const [currentStart, currentEnd] = sorted[i];
        const [, lastEnd] = merged[merged.length - 1];

        if (currentStart <= lastEnd) {
            merged[merged.length - 1][1] =
                currentEnd > lastEnd ? currentEnd : lastEnd;
        } else {
            merged.push([currentStart, currentEnd]);
        }
    }
    return merged;
}

/**
 * Parses and separates disabled date entries into individual dates and ranges.
 * Overlapping ranges are automatically merged.
 */
export function parseDisabledDates(disabled_dates?: (string | string[])[]): {
    parsedDisabledDates?: Date[];
    parsedDisabledRanges?: [Date, Date][];
} {
    if (!disabled_dates) {
        return {};
    }

    const dates: Date[] = [];
    const ranges: [Date, Date][] = [];

    for (const entry of disabled_dates) {
        if (Array.isArray(entry)) {
            const start = strAsDate(entry[0]);
            const end = strAsDate(entry[1]);
            if (start && end) {
                ranges.push([start, end]);
            }
        } else {
            const date = strAsDate(entry);
            if (date) {
                dates.push(date);
            }
        }
    }
    const mergedRanges = ranges.length > 0 ? mergeRanges(ranges) : undefined;
    const filteredDates = dates.filter(
        date =>
            !mergedRanges?.some(([start, end]) =>
                isDateInRange(date, start, end)
            )
    );
    return {
        parsedDisabledDates:
            filteredDates.length > 0 ? filteredDates : undefined,
        parsedDisabledRanges: mergedRanges,
    };
}

export function expandDisableFlags(
    flags:
        | DisableDatesFlag
        | DisablePredicate
        | Array<DisableDatesFlag | DisablePredicate>,
    minDate: Date,
    maxDate: Date
): {dates: Date[]; ranges: [Date, Date][]} {
    const disabled: Date[] = [];
    for (let d = startOfDay(minDate); d <= maxDate; d = addDays(d, 1)) {
        if (
            isDateDisabled(d, undefined, undefined, undefined, undefined, flags)
        ) {
            disabled.push(d);
        }
    }

    const groups: Date[][] = [];
    for (const d of disabled) {
        const last = groups[groups.length - 1];
        if (
            last &&
            addDays(last[last.length - 1], 1).getTime() === d.getTime()
        ) {
            last.push(d);
        } else {
            groups.push([d]);
        }
    }

    const dates: Date[] = [];
    const ranges: [Date, Date][] = [];
    for (const group of groups) {
        if (group.length > 1) {
            ranges.push([group[0], group[group.length - 1]]);
        } else {
            dates.push(group[0]);
        }
    }

    return {dates, ranges};
}

/**
 * Finds the nearest valid date according to min/max bounds,
 * disabled dates, disabled ranges, and disable flags.
 * If the provided date is already valid, it is returned unchanged.
 * When inside a disabled range, the function snaps to the closest
 * valid boundary outside that range.
 * Otherwise, the function searches incrementally forward/backward
 * for the nearest valid date.
 */
export function snapToValidDate(
    date: Date,
    step?: number | null,
    stepUnit?: DateStepUnit | null,
    minDate?: Date,
    maxDate?: Date,
    disabledDates?: Date[],
    disabledRanges?: [Date, Date][],
    disableFlags?:
        | DisableDatesFlag
        | DisablePredicate
        | Array<DisableDatesFlag | DisablePredicate>,
    marks?: DateSliderMarks | null
): Date {
    const MAX_SEARCH = 1000;
    const s = step ?? 1;
    const u = stepUnit ?? 'days';

    const markTimestamps: number[] | undefined =
        !step && marks
            ? Object.keys(marks)
                  .map(dateStringToTimestamp)
                  .filter((ts): ts is number => typeof ts === 'number')
                  .sort((a, b) => a - b)
            : undefined;

    const nextStep = (d: Date, dir: 'fwd' | 'bwd'): Date | undefined => {
        if (markTimestamps) {
            const ts = d.getTime();
            if (dir === 'fwd') {
                const found = markTimestamps.find(m => m > ts);
                return found ? new Date(found) : undefined;
            }

            const found = [...markTimestamps].reverse().find(m => m < ts);
            return found ? new Date(found) : undefined;
        }
        return stepDate(d, dir === 'fwd' ? s : -s, u);
    };

    const snapGrid = (d: Date, anchor: Date): Date => {
        if (markTimestamps) {
            const ts = d.getTime();
            const best = markTimestamps.reduce((a, b) =>
                Math.abs(a - ts) <= Math.abs(b - ts) ? a : b
            );
            return new Date(best);
        }
        return snapToStep(d, anchor, s, u);
    };

    const anchor = minDate ?? date;
    const gridDate = snapGrid(date, anchor);

    if (
        !isDateDisabled(
            gridDate,
            minDate,
            maxDate,
            disabledDates,
            disabledRanges,
            disableFlags
        )
    ) {
        return gridDate;
    }

    const walkToValid = (
        candidate: Date,
        direction: 'before' | 'after'
    ): Date | undefined => {
        const dir = direction === 'before' ? 'bwd' : 'fwd';
        const boundOk = (d: Date) =>
            direction === 'before'
                ? !minDate || d >= minDate
                : !maxDate || d <= maxDate;
        let d = snapGrid(candidate, anchor);
        if (direction === 'before' && d > candidate) {
            d = nextStep(d, 'bwd') ?? d;
        }
        if (direction === 'after' && d < candidate) {
            d = nextStep(d, 'fwd') ?? d;
        }
        for (let i = 0; i < MAX_SEARCH; i++) {
            if (
                !isDateDisabled(
                    d,
                    minDate,
                    maxDate,
                    disabledDates,
                    disabledRanges,
                    disableFlags
                ) &&
                boundOk(d)
            ) {
                return d;
            }
            const next = nextStep(d, dir);
            if (!next) {
                break;
            }
            d = next;
        }
        return undefined;
    };

    const containingRange = disabledRanges?.find(([start, end]) =>
        isDateInRange(gridDate, start, end)
    );
    if (containingRange) {
        const [start, end] = containingRange;
        const firstAfter = (() => {
            const snapped = snapGrid(end, anchor);
            return snapped > end
                ? snapped
                : nextStep(snapped, 'fwd') ?? undefined;
        })();
        const firstBefore = (() => {
            const snapped = snapGrid(start, anchor);
            return snapped < start
                ? snapped
                : nextStep(snapped, 'bwd') ?? undefined;
        })();
        const validBefore = firstBefore
            ? walkToValid(firstBefore, 'before')
            : undefined;
        const validAfter = firstAfter
            ? walkToValid(firstAfter, 'after')
            : undefined;
        if (validBefore && validAfter) {
            const distBefore = Math.abs(
                differenceInDays(gridDate, validBefore)
            );
            const distAfter = Math.abs(differenceInDays(gridDate, validAfter));
            return distBefore <= distAfter ? validBefore : validAfter;
        }
        return validBefore ?? validAfter ?? gridDate;
    }

    const forward = walkToValid(gridDate, 'after');
    const backward = walkToValid(gridDate, 'before');
    if (forward && backward) {
        const distForward = Math.abs(differenceInDays(gridDate, forward));
        const distBackward = Math.abs(differenceInDays(gridDate, backward));
        return distForward <= distBackward ? forward : backward;
    }
    return backward ?? forward ?? gridDate;
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

/**
 * Ensures a range expansion does not cross disabled constraints.
 * The expanded side is preserved and the opposite side is pulled
 * inward minimally to avoid disabled intersections.
 */
export function enforceNoDisabledInBetween(
    newDates: [string, string],
    prevDates: [string, string],
    minDate?: Date,
    maxDate?: Date,
    disabledDates?: Date[],
    disabledRanges?: [Date, Date][],
    disableFlags?:
        | DisableDatesFlag
        | DisablePredicate
        | Array<DisableDatesFlag | DisablePredicate>,
    step?: number | null,
    stepUnit?: DateStepUnit | null,
    marks?: DateSliderMarks | null
): [string, string] {
    const s = step ?? 1;
    const u = stepUnit ?? 'days';

    // If marks, use mark timestamps as the valid steps
    const markTimestamps: number[] | undefined =
        !step && marks
            ? Object.keys(marks)
                  .map(dateStringToTimestamp)
                  .filter((ts): ts is number => typeof ts === 'number')
                  .sort((a, b) => a - b)
            : undefined;

    const nextStep = (date: Date, dir: 'fwd' | 'bwd'): Date | undefined => {
        if (markTimestamps) {
            const ts = date.getTime();
            if (dir === 'fwd') {
                const found = markTimestamps.find(m => m > ts);
                return found ? new Date(found) : undefined;
            }

            const found = [...markTimestamps].reverse().find(m => m < ts);
            return found ? new Date(found) : undefined;
        }
        return stepDate(date, dir === 'fwd' ? s : -s, u);
    };

    const [newLeftStr, newRightStr] = newDates;
    const [prevLeftStr, prevRightStr] = prevDates;

    const newLeft = strAsDate(newLeftStr);
    const newRight = strAsDate(newRightStr);
    const prevLeft = strAsDate(prevLeftStr);
    const prevRight = strAsDate(prevRightStr);

    if (!newLeft || !newRight || !prevLeft || !prevRight) {
        return newDates;
    }
    const leftChanged = newLeft < prevLeft || newLeft > prevLeft;
    const rightChanged = newRight < prevRight || newRight > prevRight;

    if (!leftChanged && !rightChanged) {
        return newDates;
    }

    const walkFlags = (start: Date, end: Date, dir: 'fwd' | 'bwd'): Date => {
        if (
            !disableFlags ||
            (Array.isArray(disableFlags) && disableFlags.length === 0)
        ) {
            return end;
        }
        let d: Date | undefined = start;
        while (d && (dir === 'fwd' ? d < end : d > end)) {
            if (
                isDateDisabled(
                    d,
                    undefined,
                    undefined,
                    undefined,
                    undefined,
                    disableFlags
                )
            ) {
                return d;
            }
            d = nextStep(d, dir);
        }
        return end;
    };

    if (leftChanged) {
        if (
            isDateDisabled(
                newLeft,
                minDate,
                maxDate,
                disabledDates,
                disabledRanges,
                disableFlags
            )
        ) {
            return [newLeftStr, newLeftStr];
        }
        let clampRight = nextStep(newRight, 'fwd') ?? newRight;
        for (const candidate of [
            ...(disabledRanges?.map(([start]) => start) ?? []),
            ...(disabledDates ?? []),
        ]) {
            if (
                candidate > newLeft &&
                candidate <= newRight &&
                candidate < clampRight
            ) {
                clampRight = candidate;
            }
        }
        clampRight = walkFlags(newLeft, clampRight, 'fwd');
        clampRight = nextStep(clampRight, 'bwd') ?? clampRight;
        if (clampRight < newLeft) {
            return [newLeftStr, newLeftStr];
        }
        const rightStr = timestampToDateString(clampRight.getTime());
        return rightStr ? [newLeftStr, rightStr] : newDates;
    }
    if (
        isDateDisabled(
            newRight,
            minDate,
            maxDate,
            disabledDates,
            disabledRanges,
            disableFlags
        )
    ) {
        return [newRightStr, newRightStr];
    }
    let clampLeft = nextStep(newLeft, 'bwd') ?? newLeft;
    for (const candidate of [
        ...(disabledRanges?.map(([, end]) => end) ?? []),
        ...(disabledDates ?? []),
    ]) {
        if (
            candidate < newRight &&
            candidate >= newLeft &&
            candidate > clampLeft
        ) {
            clampLeft = candidate;
        }
    }
    clampLeft = walkFlags(newRight, clampLeft, 'bwd');
    clampLeft = nextStep(clampLeft, 'fwd') ?? clampLeft;
    if (clampLeft > newRight) {
        return [newRightStr, newRightStr];
    }
    const leftStr = timestampToDateString(clampLeft.getTime());
    return leftStr ? [leftStr, newRightStr] : newDates;
}
