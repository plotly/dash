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

const estimateBestSteps = (
    minValue: number,
    maxValue: number,
    stepValue: number,
    sliderWidth?: number | null
) => {
    // Base desired count for 330px slider with 0-100 scale (10 marks = 11 total including endpoints)
    let targetMarkCount = 11; // Default baseline

    // Scale mark density based on slider width
    if (sliderWidth) {
        const baselineWidth = 330;
        const baselineMarkCount = 11; // 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100

        // Calculate density multiplier based on width
        const widthMultiplier = sliderWidth / baselineWidth;

        // Target mark count scales with width but maintains consistent density
        // The range adjustment should be removed - we want consistent mark density based on width
        targetMarkCount = Math.round(baselineMarkCount * widthMultiplier);

        // Ensure reasonable bounds
        const UPPER_BOUND = 50;
        targetMarkCount = Math.max(3, Math.min(targetMarkCount, UPPER_BOUND));

        // Adjust density based on maximum character width of mark labels
        // Estimate the maximum characters in any mark label
        const maxValueChars = Math.max(
            String(minValue).length,
            String(maxValue).length,
            String(Math.abs(minValue)).length,
            String(Math.abs(maxValue)).length
        );

        // Baseline: 3-4 characters (like "100", "250") work well with baseline density
        // For longer labels, reduce density to prevent overlap
        const baselineChars = 3.5;
        if (maxValueChars > baselineChars) {
            const charReductionFactor = baselineChars / maxValueChars;
            targetMarkCount = Math.round(targetMarkCount * charReductionFactor);
            targetMarkCount = Math.max(2, targetMarkCount); // Ensure minimum of 2 marks
        }
    }

    // Calculate the ideal interval between marks based on target count
    const range = maxValue - minValue;
    let idealInterval = range / (targetMarkCount - 1);

    // Check if the step value is fractional and adjust density
    if (stepValue % 1 !== 0) {
        // For fractional steps, reduce mark density by half to avoid clutter
        targetMarkCount = Math.max(3, Math.round(targetMarkCount / 2));
        idealInterval = range / (targetMarkCount - 1);
    }

    // Find the best interval that's a multiple of stepValue
    // Start with multiples of stepValue and find the one closest to idealInterval
    const stepMultipliers = [
        // eslint-disable-next-line no-magic-numbers
        1, 2, 2.5, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000,
    ];

    let bestInterval = stepValue;
    let bestDifference = Math.abs(idealInterval - stepValue);

    for (const multiplier of stepMultipliers) {
        const candidateInterval = stepValue * multiplier;
        const difference = Math.abs(idealInterval - candidateInterval);

        if (difference < bestDifference) {
            bestInterval = candidateInterval;
            bestDifference = difference;
        }

        // Stop if we've gone too far beyond the ideal
        if (candidateInterval > idealInterval * 2) {
            break;
        }
    }

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

export const applyD3Format = (mark: number, min: number, max: number) => {
    const mu_ten_factor = -3;
    const k_ten_factor = 3;

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

export const autoGenerateMarks = (
    min: number,
    max: number,
    step?: number | null,
    sliderWidth?: number | null
) => {
    const marks = [];
    // Always use dynamic logic, but pass the provided step as a constraint
    const effectiveStep = step || calcStep(min, max, 0);
    const [start, interval, chosenStep] = estimateBestSteps(
        min,
        max,
        effectiveStep,
        sliderWidth
    );
    let cursor = start;

    // Apply a safety cap to prevent excessive mark generation while preserving existing behavior
    // Only restrict when marks would be truly excessive (much higher than the existing UPPER_BOUND)
    const MARK_WIDTH_PX = 20; // More generous spacing for width-based calculation
    const FALLBACK_MAX_MARKS = 200; // High fallback to preserve existing behavior when no width
    const ABSOLUTE_MAX_MARKS = 200; // Safety cap against extreme cases

    const widthBasedMax = sliderWidth
        ? Math.max(10, Math.floor(sliderWidth / MARK_WIDTH_PX))
        : FALLBACK_MAX_MARKS;

    const maxAutoGeneratedMarks = Math.min(widthBasedMax, ABSOLUTE_MAX_MARKS);

    // Calculate how many marks would be generated with current interval
    const estimatedMarkCount = Math.floor((max - start) / interval) + 1;

    // If we would exceed the limit, increase the interval to fit within the limit
    let actualInterval = interval;
    if (estimatedMarkCount > maxAutoGeneratedMarks) {
        // Recalculate interval to fit exactly within the limit
        actualInterval = (max - start) / (maxAutoGeneratedMarks - 1);
        // Round to a reasonable step multiple to keep marks clean
        const stepMultiple = Math.ceil(actualInterval / chosenStep);
        actualInterval = stepMultiple * chosenStep;
    }

    if ((max - cursor) / actualInterval > 0) {
        do {
            marks.push(alignValue(cursor, chosenStep));
            cursor += actualInterval;
        } while (cursor < max && marks.length < maxAutoGeneratedMarks);

        // do some cosmetic
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
