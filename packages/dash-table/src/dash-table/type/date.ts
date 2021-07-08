import {
    IDatetimeColumn,
    IDateValidation
} from 'dash-table/components/Table/props';
import {reconcileNull} from './null';
import {IReconciliation} from './reconcile';

// pattern and convertToMs pulled from plotly.js
// (simplified - no international calendars for now)
// https://github.com/plotly/plotly.js/blob/master/src/lib/dates.js
// Note we allow timezone info but ignore it - at least for now.
const DATETIME_REGEXP =
    /^\s*(-?\d{4}|\d{2})(-(\d{1,2})(-(\d{1,2})([ Tt]([01]?\d|2[0-3])(:([0-5]\d)(:([0-5]\d(\.\d+)?))?(Z|z|[+\-]\d{2}:?\d{2})?)?)?)?)?\s*$/m;

// for 2-digit years, the first year we map them onto
// Also pulled from plotly.js - see discussion there for details
// Please don't use 2-digit years!
const YFIRST = new Date().getFullYear() - 70;

export function normalizeDate(
    value: any,
    options?: IDateValidation
): string | null {
    // unlike plotly.js, do not accept year as a number - only strings.
    if (typeof value !== 'string') {
        return null;
    }

    const match = value.match(DATETIME_REGEXP);
    if (!match) {
        return null;
    }

    const yearMatch = match[1];
    const YY = yearMatch.length === 2;

    if (YY && !(options && options.allow_YY)) {
        return null;
    }

    const y = YY
        ? ((Number(yearMatch) + 2000 - YFIRST) % 100) + YFIRST
        : Number(yearMatch);
    const BCE = y < 0;

    // js Date objects have months 0-11, not 1-12
    const monthMatch = match[3];
    const m = Number(monthMatch || '1') - 1;

    const dayMatch = match[5];
    const d = Number(dayMatch || 1);

    const hourMatch = match[7];
    const H = Number(hourMatch || 0);

    const minuteMatch = match[9];
    const M = Number(minuteMatch || 0);

    // includes fractional seconds - but omitted from the
    // Date constructor because it clips to milliseconds.
    const secondMatch = match[11];

    // javascript takes new Date(0..99,m,d) to mean 1900-1999, so
    // to support years 0-99 we need to use setFullYear explicitly
    // Note that 2000 is a leap year.
    const date = new Date(Date.UTC(2000, m, d, H, M));
    date.setUTCFullYear(y);

    // The regexp catches most faulty dates & times, but invalid month/day
    // combinations will show up here
    if (date.getUTCMonth() !== m || date.getUTCDate() !== d) {
        return null;
    }

    // standardize the string format
    // for negative years, toISOString gives six digits (and the minus sign)
    // but we only want 4, and we'll put the minus sign back later.
    const fullDateStr =
        date
            .toISOString()
            .substr(BCE ? 3 : 0, 17)
            .replace('T', ' ') + (secondMatch || '');

    // but only include fields the user had in their original input
    const finalLen = secondMatch
        ? 29 // max 9 digits of fractional seconds
        : minuteMatch
        ? 16
        : hourMatch
        ? 13
        : dayMatch
        ? 10
        : monthMatch
        ? 7
        : 4;

    return (BCE ? '-' : '') + fullDateStr.substr(0, finalLen);
}

export function coerce(
    value: any,
    options: IDatetimeColumn | undefined
): IReconciliation {
    const normalizedDate = normalizeDate(value, options && options.validation);
    return normalizedDate !== null
        ? {
              success: true,
              value: normalizedDate
          }
        : reconcileNull(value, options);
}

export function validate(
    value: any,
    options: IDatetimeColumn | undefined
): IReconciliation {
    return typeof value === 'string' &&
        normalizeDate(value, options && options.validation) !== null
        ? {success: true, value: value.trim()}
        : reconcileNull(value, options);
}
