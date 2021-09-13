import {pickBy} from 'ramda';

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
    ];
};

export const autoGenerateMarks = (min, max, step = 1) => {
    const marks = [];
    const [start, interval] = estimateBestSteps(min, max, step);
    let cursor = start + interval;

    do {
        marks.push(alignValue(cursor, step));
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

    const marksObject = {};
    marks.forEach(mark => {
        marksObject[mark] = String(mark);
    });
    marksObject[min] = `Start (${min})`;
    marksObject[max] = `End (${max})`;
    return marksObject;
};

/**
 * Set marks to min and max if not defined, truncate otherwise
 */
export const calcMarks = ({min, max, marks, step}) => {
    return truncateMarks(
        min,
        max,
        marks ? marks : autoGenerateMarks(min, max, step)
    );
};

/**
 * Calculate default step if not defined
 */
export const calcStep = (min, max, step) => {
    if (step !== undefined) {
        return step;
    }

    const size = Math.abs(max - min); // interval size
    /**
     * Size multiplied by 10^i to get a nice step value at the end (0.1, 1, 10, 100, ...)
     */
    const divident = size
        .toString()
        .replace('.', '') // removes decimal point
        .replace(/^(\d*?[1-9])0+$/, '$1'); // removes trailing zeros

    return size / divident;
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