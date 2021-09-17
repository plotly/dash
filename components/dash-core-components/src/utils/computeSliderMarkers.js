import {pickBy, isEmpty} from 'ramda';
import {formatPrefix} from 'd3-format';

/**
 * Truncate marks if they are out of Slider interval
 */
const truncateMarks = (min, max, marks) =>
    pickBy((k, mark) => mark >= min && mark <= max, marks);

const truncateNumber = num =>
    parseInt(num.toString().match(/^-?\d+(?:\.\d{0,0})?/)[0], 10);

const decimalCount = d =>
    String(d).split('.').length > 1 ? String(d).split('.')[1].length : 0;
const alignIntValue = (v, d) =>
    d < 10
        ? v
        : parseInt((truncateNumber(v / d) * d).toFixed(decimalCount(d)), 10);
const alignDecimalValue = (v, d) =>
    d < 10
        ? parseFloat(v.toFixed(decimalCount(d)))
        : parseFloat(((v / d).toFixed(0) * d).toFixed(decimalCount(d)));

const alignValue = (v, d) =>
    decimalCount(d) < 1 ? alignIntValue(v, d) : alignDecimalValue(v, d);

const log = v => Math.floor(Math.log10(v));

const getNearByStep = v =>
    v < 10
        ? [v]
        : [
              Math.pow(10, Math.floor(Math.log10(v))),
              Math.pow(10, Math.ceil(Math.log10(v))) / 2,
              alignValue(v, Math.pow(10, log(v))),
              Math.pow(10, Math.ceil(Math.log10(v))),
          ].sort((a, b) => Math.abs(a - v) - Math.abs(b - v));

const estimateBestSteps = (minValue, maxValue, stepValue) => {
    const desiredCountMin = 2 + (maxValue / stepValue <= 10 ? 3 : 3); // including start, end
    const desiredCountMax = 2 + (maxValue / stepValue <= 10 ? 4 : 6);

    const min = minValue / stepValue;
    const max = maxValue / stepValue;

    const rangeLength = max - min;

    const leastMarksInterval = Math.max(
        Math.round(rangeLength / (desiredCountMin - 1)),
        1
    );
    const possibleValues = getNearByStep(leastMarksInterval);

    const finalStep =
        possibleValues.find(step => {
            const expectedSteps = Math.ceil(rangeLength / step) + 1;
            return (
                expectedSteps >= desiredCountMin - 1 &&
                expectedSteps <= desiredCountMax + 1
            );
        }) || possibleValues[0];
    return [
        alignValue(min, finalStep) * stepValue,
        alignValue(finalStep * stepValue, stepValue),
        stepValue,
    ];
};

/**
 * Calculate default step if not defined
 */
export const calcStep = (min, max, step) => {
    if (step) {
        return step;
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

export const autoGenerateMarks = (min, max, step) => {
    const max_min_mean = (Math.abs(max) + Math.abs(min)) / 2;
    const marks = [];
    const [start, interval, chosenStep] = step
        ? [min, step, step]
        : estimateBestSteps(min, max, calcStep(min, max, step));
    let cursor = start + interval;

    // make sure we don't step into infinite loop
    if ((max - cursor) / interval > 0) {
        do {
            marks.push(alignValue(cursor, chosenStep));
            cursor += interval;
        } while (cursor < max);

        // do some cosmetic
        const discardThreshold = 1.5;
        if (
            marks.length >= 2 &&
            max - marks[marks.length - 2] <= interval * discardThreshold
        ) {
            marks.pop();
        }
    }

    const marksObject = {};
    const si_formatter = formatPrefix(',.0', max_min_mean);
    marks.forEach(mark => {
        marksObject[mark] = String(si_formatter(mark));
    });
    marksObject[min] = String(si_formatter(min));
    marksObject[max] = String(si_formatter(max));
    return marksObject;
};

/**
 * - Auto generate marks if not given,
 * - Then truncate marks so no out of range marks
 */
export const sanitizeMarks = ({min, max, marks, step}) => {
    const truncated_marks =
        marks && isEmpty(marks) === false
            ? truncateMarks(min, max, marks)
            : marks;

    if (truncated_marks && isEmpty(truncated_marks) === false) {
        return truncated_marks;
    }
    return autoGenerateMarks(min, max, step);
};

/**
 * Calculate default value if not defined
 */
export const calcValue = (min, max, value) => {
    if (value !== undefined) {
        return value;
    }

    return [min, max];
};
