import React from 'react';
import {SliderMarks} from '../types';

// Replicate Radix UI's exact positioning logic for displaying marks
const convertValueToPercentage = (value: number, min: number, max: number) => {
    const maxSteps = max - min;
    const percentPerStep = 100 / maxSteps;
    const percentage = percentPerStep * (value - min);
    // Clamp to 0-100 range like Radix does
    return Math.max(0, Math.min(100, percentage));
};

const linearScale = (
    input: readonly [number, number],
    output: readonly [number, number]
) => {
    return (value: number) => {
        if (input[0] === input[1] || output[0] === output[1]) {
            return output[0];
        }
        const ratio = (output[1] - output[0]) / (input[1] - input[0]);
        return output[0] + ratio * (value - input[0]);
    };
};

const getThumbInBoundsOffset = (
    width: number,
    left: number,
    direction: number
) => {
    const halfWidth = width / 2;
    const halfPercent = 50;
    const offset = linearScale([0, halfPercent], [0, halfWidth]);
    return (halfWidth - offset(left) * direction) * direction;
};

// Calculate the exact position including pixel offset as Radix does
const getRadixThumbPosition = (
    value: number,
    minMaxValues: {min_mark: number; max_mark: number},
    thumbWidth = 16
) => {
    const percentage = convertValueToPercentage(
        value,
        minMaxValues.min_mark,
        minMaxValues.max_mark
    );
    const direction = 1; // LTR direction
    const thumbInBoundsOffset = getThumbInBoundsOffset(
        thumbWidth,
        percentage,
        direction
    );
    return {percentage, offset: thumbInBoundsOffset};
};

export const renderSliderMarks = (
    renderedMarks: SliderMarks,
    vertical: boolean,
    minMaxValues: {min_mark: number; max_mark: number},
    selectedValues: number[] = [],
    dots: boolean,
    reverse = false
) => {
    return Object.entries(renderedMarks).map(([position, mark]) => {
        const pos = parseFloat(position);

        // When reversed, use the inverted value for positioning
        const displayPos = reverse
            ? minMaxValues.max_mark - pos + minMaxValues.min_mark
            : pos;

        const thumbPosition = getRadixThumbPosition(displayPos, minMaxValues);

        const style = vertical
            ? {
                  bottom: `calc(${thumbPosition.percentage}% + ${thumbPosition.offset}px - 13px)`,
                  left: 'calc(100% + 8px)',
                  transform: 'translateY(-50%)',
              }
            : {
                  left: `calc(${thumbPosition.percentage}% + ${thumbPosition.offset}px)`,
                  bottom: 0,
                  transform: 'translateX(-50%)',
              };

        // Determine if mark is outside the selected range
        let isOutsideSelection = false;
        if (selectedValues.length === 1) {
            isOutsideSelection = pos > selectedValues[0];
        } else if (selectedValues.length > 1) {
            const [minValue, maxValue] = [
                selectedValues[0],
                selectedValues[selectedValues.length - 1],
            ];
            isOutsideSelection = pos < minValue || pos > maxValue;
        }

        const outsideClassName = isOutsideSelection
            ? 'dash-slider-mark-outside-selection'
            : '';

        const className = `dash-slider-mark ${
            dots ? 'with-dots' : ''
        } ${outsideClassName}`.trim();

        return (
            <div
                key={position}
                className={className}
                style={{
                    ...style,
                    ...(typeof mark === 'object' && mark.style
                        ? mark.style
                        : {}),
                }}
            >
                {typeof mark === 'string' ? mark : mark?.label || pos}
            </div>
        );
    });
};

export const renderSliderDots = (
    stepValue: number,
    minMaxValues: {min_mark: number; max_mark: number},
    selectedValues: number[] = [],
    vertical: boolean,
    reverse = false
) => {
    if (stepValue <= 1) {
        return null;
    }

    const dotCount =
        Math.floor(
            (minMaxValues.max_mark - minMaxValues.min_mark) / stepValue
        ) + 1;

    // Cap at 100 dots - if more, don't render any dots
    if (dotCount > 100) {
        return null;
    }

    return Array.from(
        {
            length: dotCount,
        },
        (_, i) => {
            const dotValue = minMaxValues.min_mark + i * stepValue;

            // When reversed, use the inverted value for positioning
            const displayValue = reverse
                ? minMaxValues.max_mark - dotValue + minMaxValues.min_mark
                : dotValue;

            const thumbPosition = getRadixThumbPosition(
                displayValue,
                minMaxValues
            );

            const dotStyle = vertical
                ? {
                      bottom: `calc(${thumbPosition.percentage}% + ${thumbPosition.offset}px)`,
                      left: '2px',
                      transform: 'translate(50%, 50%)',
                  }
                : {
                      left: `calc(${thumbPosition.percentage}% + ${thumbPosition.offset}px)`,
                      top: '0',
                      transform: 'translate(-50%, 50%)',
                  };

            // Determine if dot is outside the selected range
            let isOutsideSelection = false;
            if (selectedValues.length === 1) {
                isOutsideSelection = dotValue > selectedValues[0];
            } else if (selectedValues.length > 1) {
                const [minValue, maxValue] = [
                    selectedValues[0],
                    selectedValues[selectedValues.length - 1],
                ];
                isOutsideSelection = dotValue < minValue || dotValue > maxValue;
            }

            const className = isOutsideSelection
                ? 'dash-slider-dot dash-slider-dot-outside-selection'
                : 'dash-slider-dot';

            return (
                <div
                    key={i}
                    className={className}
                    style={{
                        ...dotStyle,
                    }}
                />
            );
        }
    );
};
