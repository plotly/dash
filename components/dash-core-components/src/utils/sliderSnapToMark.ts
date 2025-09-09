import {SliderMarks} from '../types';

export const snapToNearestMark = (
    value: number,
    marks: SliderMarks
): number => {
    const markValues = Object.keys(marks).map(Number);
    if (markValues.length === 0) {
        return value;
    }

    return markValues.reduce((closest, current) => {
        return Math.abs(current - value) < Math.abs(closest - value)
            ? current
            : closest;
    });
};
