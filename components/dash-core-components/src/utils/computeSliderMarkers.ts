/* eslint-disable no-magic-numbers */
import {pickBy, isEmpty, isNil} from 'ramda';
import {formatPrefix} from 'd3-format';
import {SliderMarks} from '../types';

/**
 * Truncate marks if they are out of Slider interval
 */
const truncateMarks = (
    min: number,
    max: number,
    marks: SliderMarks
): SliderMarks => pickBy((k, mark) => mark >= min && mark <= max, marks);

const truncateNumber = (num: number) => {
    const match = num.toString().match(/^-?\d+(?:\.\d{0,0})?/);
    return match ? parseInt(match[0], 10) : 0;
};

const decimalCount = (d: number) =>
    String(d).split('.').length > 1 ? String(d).split('.')[1].length : 0;
const alignIntValue = (v: number, d: number) =>
    d < 10
        ? v
        : parseInt((truncateNumber(v / d) * d).toFixed(decimalCount(d)), 10);
const alignDecimalValue = (v: number, d: number) =>
    d < 10
        ? parseFloat(v.toFixed(decimalCount(d)))
        : parseFloat(
              (parseFloat((v / d).toFixed(0)) * d).toFixed(decimalCount(d))
          );

const alignValue = (v: number, d: number) =>
    decimalCount(d) < 1 ? alignIntValue(v, d) : alignDecimalValue(v, d);

export const applyD3Format = (mark: number, min: number, max: number) => {
    const mu_ten_factor = -3;
    const k_ten_factor = 4; // values < 10000 don't get formatted

    const ten_factor = Math.log10(Math.abs(mark));
    if (
        mark === 0 ||
        (ten_factor > mu_ten_factor && ten_factor < k_ten_factor)
    ) {
        return String(mark);
    }
    const max_min_mean = (Math.abs(max) + Math.abs(min)) / 2;
    const si_formatter = formatPrefix(',.0', max_min_mean);
    return String(si_formatter(mark));
};

const estimateBestSteps = (
    minValue: number,
    maxValue: number,
    stepValue: number,
    sliderWidth?: number | null
) => {
    // Use formatted label length to account for SI formatting
    // (e.g. labels that look like "100M" vs "100000000")
    const formattedMin = applyD3Format(minValue, minValue, maxValue);
    const formattedMax = applyD3Format(maxValue, minValue, maxValue);
    const maxValueChars = Math.max(formattedMin.length, formattedMax.length);

    // Calculate required spacing based on label width
    // Estimate: 10px per character + 20px margin for spacing between labels
    // This provides comfortable spacing to prevent overlap
    const pixelsPerChar = 10;
    const spacingMargin = 20;
    const minPixelsPerMark = maxValueChars * pixelsPerChar + spacingMargin;

    const effectiveWidth = sliderWidth || 330;

    // Calculate maximum number of marks that can fit without overlap
    let targetMarkCount = Math.floor(effectiveWidth / minPixelsPerMark) + 1;
    targetMarkCount = Math.max(3, Math.min(targetMarkCount, 50));

    // Calculate the ideal interval between marks based on target count
    const range = maxValue - minValue;
    const idealInterval = range / (targetMarkCount - 1);

    // Calculate the multiplier needed to get close to idealInterval
    // Round to a "nice" number for cleaner mark placement
    const rawMultiplier = idealInterval / stepValue;

    // Round to nearest nice multiplier (1, 2, 2.5, 5, or power of 10 multiple)
    const magnitude = Math.pow(10, Math.floor(Math.log10(rawMultiplier)));
    const normalized = rawMultiplier / magnitude; // Now between 1 and 10

    let niceMultiplier;
    if (normalized <= 1.5) {
        niceMultiplier = 1;
    } else if (normalized <= 2.25) {
        niceMultiplier = 2;
    } else if (normalized <= 3.5) {
        niceMultiplier = 2.5;
    } else if (normalized <= 5) {
        niceMultiplier = 5;
    } else {
        niceMultiplier = 10;
    }

    const bestMultiplier = Math.max(1, niceMultiplier * magnitude);
    const bestInterval = stepValue * bestMultiplier;

    // All marks must be at valid step positions: minValue + (n * stepValue)
    // Find the first mark after minValue that fits our desired interval
    const stepsInInterval = Math.round(bestInterval / stepValue);
    const actualInterval = stepsInInterval * stepValue;

    // Find the first mark position that's aligned with our interval
    // This ensures we don't have overlapping marks at narrow widths
    const firstMarkSteps = Math.max(1, stepsInInterval);
    const firstStepAfterMin = minValue + firstMarkSteps * stepValue;

    return [firstStepAfterMin, actualInterval, stepValue];
};

/**
 * Calculate default step if not defined
 */
export const calcStep = (min?: number, max?: number, step?: number | null) => {
    if (step) {
        return step;
    }

    if (isNil(min) || isNil(max)) {
        return 1;
    }

    const diff = max > min ? max - min : min - max;

    const v = (Math.abs(diff) + Number.EPSILON) / 100;
    const N = Math.floor(Math.log10(v));
    return [
        Number(Math.pow(10, N)),
        2 * Math.pow(10, N),
        5 * Math.pow(10, N),
    ].sort((a, b) => Math.abs(a - v) - Math.abs(b - v))[0];
};

/**
 * Set min and max if they are undefined and marks are defined
 */
export const setUndefined = (
    min: number | undefined,
    max: number | undefined,
    marks: SliderMarks | undefined | null
) => {
    const definedMarks = {min_mark: min ?? 0, max_mark: max ?? 1};

    if (isNil(marks)) {
        return definedMarks;
    }

    const marksObject = Object.keys(marks).map(Number);

    if (isNil(min)) {
        definedMarks.min_mark = Math.min(...marksObject);
    }

    if (isNil(max)) {
        definedMarks.max_mark = Math.max(...marksObject);
    }

    return definedMarks;
};

export const autoGenerateMarks = (
    min: number,
    max: number,
    step?: number | null,
    sliderWidth?: number | null
) => {
    const marks = [];

    const effectiveStep = step ?? 1;

    const [start, interval, chosenStep] = estimateBestSteps(
        min,
        max,
        effectiveStep,
        sliderWidth
    );
    let cursor = start;

    if ((max - cursor) / interval > 0) {
        while (cursor < max) {
            marks.push(alignValue(cursor, chosenStep));
            const prevCursor = cursor;
            cursor += interval;

            // Safety check: floating point precision could impact this loop
            if (cursor <= prevCursor) {
                break;
            }
        }

        const discardThreshold = 1.5;
        if (
            marks.length >= 2 &&
            max - marks[marks.length - 2] <= interval * discardThreshold
        ) {
            marks.pop();
        }
    }
    const marksObject: SliderMarks = {};
    marks.forEach(mark => {
        marksObject[mark] = applyD3Format(mark, min, max);
    });
    marksObject[min] = applyD3Format(min, min, max);
    marksObject[max] = applyD3Format(max, min, max);
    return marksObject;
};

/**
 * - Auto generate marks if not given,
 * - Not generate anything at all when explicit null is given to marks
 * - Then truncate marks so no out of range marks
 */
type SanitizeMarksParams = {
    min?: number;
    max?: number;
    marks?: SliderMarks;
    step?: number | null;
    sliderWidth?: number | null;
};
export const sanitizeMarks = ({
    min,
    max,
    marks,
    step,
    sliderWidth,
}: SanitizeMarksParams): SliderMarks => {
    const {min_mark, max_mark} = setUndefined(min, max, marks);

    const truncated_marks =
        marks && isEmpty(marks) === false
            ? truncateMarks(min_mark, max_mark, marks)
            : marks;

    if (truncated_marks && isEmpty(truncated_marks) === false) {
        return truncated_marks;
    }

    return autoGenerateMarks(min_mark, max_mark, step, sliderWidth);
};

/**
 * Calculate default value if not defined
 */
export const calcValue = (min: number, max: number, value: unknown) => {
    if (value !== undefined) {
        return value;
    }

    return [min, max];
};
