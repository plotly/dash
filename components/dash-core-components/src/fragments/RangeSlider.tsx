import React, {useEffect, useState, useMemo, useRef} from 'react';
import * as RadixSlider from '@radix-ui/react-slider';
import {isNil} from 'ramda';

import {
    sanitizeMarks,
    calcStep,
    setUndefined,
} from '../utils/computeSliderMarkers';
import {snapToNearestMark} from '../utils/sliderSnapToMark';
import {renderSliderMarks, renderSliderDots} from '../utils/sliderRendering';
import LoadingElement from '../utils/_LoadingElement';
import {Tooltip} from '../utils/sliderTooltip';
import {RangeSliderProps} from '../types';

const MAX_MARKS = 500;

/**
 * A double slider with two handles.
 * Used for specifying a range of numerical values.
 */
export default function RangeSlider(props: RangeSliderProps) {
    const {
        className,
        id,
        setProps,
        tooltip,
        updatemode,
        min,
        max,
        marks,
        step,
        vertical,
        verticalHeight,
        value: propValue,
        disabled,
        dots,
        included,
        allowCross,
        pushable,
        count,
    } = props;

    // For range slider, we expect an array of values
    const [value, setValue] = useState<number[]>(propValue || []);

    // Track slider dimension (width for horizontal, height for vertical) for conditional input rendering
    const [sliderWidth, setSliderWidth] = useState<number | null>(null);
    const [showInputs, setShowInputs] = useState<boolean>(value.length === 2);

    const sliderRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Handle initial mount - equivalent to componentWillMount
    useEffect(() => {
        if (propValue && propValue.length > 0) {
            setProps({drag_value: propValue});
            setValue(propValue);
        } else {
            // Default to range from min to max if no value provided
            const defaultValue = [min ?? (propValue ? propValue[0] : 0)];
            setValue(defaultValue);
        }
    }, []);

    // Dynamic dimension detection using ResizeObserver (width for horizontal, height for vertical)
    useEffect(() => {
        if (!sliderRef.current) {
            return;
        }

        if (step === null) {
            // If the user has explicitly disabled stepping (step=None), then
            // the slider values are constrained to the given marks and user
            // cannot enter arbitrary values via the input element
            setShowInputs(false);
            return;
        }

        if (!value || value.length > 2) {
            setShowInputs(false);
            return;
        }

        const measureWidth = () => {
            if (sliderRef.current) {
                const rect = sliderRef.current.getBoundingClientRect();
                // Use height for vertical sliders, width for horizontal sliders
                const dimension = vertical ? rect.height : rect.width;
                if (dimension > 0) {
                    setSliderWidth(dimension);

                    // eslint-disable-next-line no-magic-numbers
                    const HIDE_AT_WIDTH = value.length === 1 ? 200 : 250;
                    // eslint-disable-next-line no-magic-numbers
                    const SHOW_AT_WIDTH = value.length === 1 ? 300 : 450;
                    if (showInputs && dimension < HIDE_AT_WIDTH) {
                        setShowInputs(false);
                    } else if (!showInputs && dimension >= SHOW_AT_WIDTH) {
                        setShowInputs(true);
                    }
                }
            }
        };

        // Initial measurement
        measureWidth();

        // Set up ResizeObserver for dynamic resizing
        const resizeObserver = new ResizeObserver(() => {
            measureWidth();
        });

        resizeObserver.observe(sliderRef.current);

        // Cleanup function when component unmounts
        // eslint-disable-next-line consistent-return
        return () => {
            resizeObserver.disconnect();
        };
    }, [showInputs, vertical, step, value]);

    // Handle prop value changes - equivalent to componentWillReceiveProps
    useEffect(() => {
        if (propValue && JSON.stringify(propValue) !== JSON.stringify(value)) {
            setProps({drag_value: propValue});
            setValue(propValue);
        }
    }, [propValue]);

    // Check if marks exceed 500 limit for performance
    let processedMarks = marks;
    if (marks && typeof marks === 'object' && marks !== null) {
        const marksCount = Object.keys(marks).length;
        if (marksCount > MAX_MARKS) {
            /* eslint-disable no-console */
            console.error(
                `Slider: Too many marks (${marksCount}) provided. ` +
                    `For performance reasons, marks are limited to 500. ` +
                    `Using auto-generated marks instead.`
            );
            processedMarks = undefined;
        }
    }

    const minMaxValues = useMemo(() => {
        return setUndefined(min, max, processedMarks);
    }, [min, max, processedMarks]);

    const stepValue = useMemo(() => {
        return step === null && isNil(processedMarks)
            ? undefined
            : calcStep(min, max, step);
    }, [min, max, processedMarks, step]);

    // Sanitize marks for rendering
    const renderedMarks = useMemo(() => {
        if (processedMarks === null) {
            return null;
        }
        return sanitizeMarks({
            min,
            max,
            marks: processedMarks,
            step,
            sliderWidth,
        });
    }, [min, max, processedMarks, step, sliderWidth]);

    // Calculate dynamic input width based on digits needed and container size
    const inputWidth = useMemo(() => {
        if (!sliderWidth) {
            return '64px'; // fallback to current width
        }

        // Count digits needed for min and max values
        const maxDigits = Math.max(
            String(Math.floor(Math.abs(minMaxValues.max_mark))).length,
            String(Math.floor(Math.abs(minMaxValues.min_mark))).length
        );

        // Add 1 for minus sign if min is negative
        const totalChars = maxDigits + (minMaxValues.min_mark < 0 ? 1 : 0);

        // Calculate width as percentage of container (5% min, 15% max)
        /* eslint-disable no-magic-numbers */
        const minWidth = sliderWidth * 0.05;
        const maxWidth = sliderWidth * 0.15;
        const charBasedWidth = totalChars * 12; // approx 12px per character
        /* eslint-enable no-magic-numbers */

        const calculatedWidth = Math.max(
            minWidth,
            Math.min(maxWidth, charBasedWidth)
        );

        // Add padding if box-sizing is border-box
        let inputPadding = 0;
        if (inputRef.current) {
            const computedStyle = window.getComputedStyle(inputRef.current);
            if (computedStyle.boxSizing === 'border-box') {
                const paddingLeft = parseFloat(computedStyle.paddingLeft) || 0;
                const paddingRight =
                    parseFloat(computedStyle.paddingRight) || 0;
                inputPadding = paddingLeft + paddingRight;
            }
        }

        const totalWidth = calculatedWidth + inputPadding;

        return `${totalWidth}px`;
    }, [sliderWidth, minMaxValues.min_mark, minMaxValues.max_mark]);

    const valueIsValid = (val: number): boolean => {
        // Check if value is within min/max bounds
        if (val < minMaxValues.min_mark || val > minMaxValues.max_mark) {
            return false;
        }

        // If step is defined, check if value aligns with step
        if (stepValue !== undefined) {
            const min = minMaxValues.min_mark;
            const offset = val - min;
            const remainder = Math.abs(offset % stepValue);
            const epsilon = 0.0001; // tolerance for floating point comparison
            if (remainder > epsilon && remainder < stepValue - epsilon) {
                return false;
            }
        }

        // If step is null and marks exist, value must match a mark
        if (
            step === null &&
            processedMarks &&
            typeof processedMarks === 'object'
        ) {
            const markValues = Object.keys(processedMarks).map(Number);
            const epsilon = 0.0001;
            return markValues.some(mark => Math.abs(val - mark) < epsilon);
        }

        return true;
    };

    const constrainToValidValue = (val: number): number => {
        // First constrain to min/max bounds
        let constrained = Math.max(
            minMaxValues.min_mark,
            Math.min(minMaxValues.max_mark, val)
        );

        // If step is null and marks exist, snap to nearest mark
        if (
            step === null &&
            processedMarks &&
            typeof processedMarks === 'object'
        ) {
            return snapToNearestMark(constrained, processedMarks);
        }

        // If step is defined, round to nearest step
        if (stepValue !== undefined) {
            const min = minMaxValues.min_mark;
            const steps = Math.round((constrained - min) / stepValue);
            constrained = min + steps * stepValue;

            // Round to avoid floating point precision issues
            // Determine decimal places from step value
            const stepStr = stepValue.toString();
            const decimalPlaces = stepStr.includes('.')
                ? stepStr.split('.')[1].length
                : 0;
            constrained = Number(constrained.toFixed(decimalPlaces));

            // Ensure we stay within bounds after rounding
            constrained = Math.max(
                minMaxValues.min_mark,
                Math.min(minMaxValues.max_mark, constrained)
            );
        }

        return constrained;
    };

    const handleValueChange = (newValue: number[]) => {
        let adjustedValue = newValue;

        // Snap to nearest marks if step is null and marks exist
        if (
            step === null &&
            processedMarks &&
            typeof processedMarks === 'object'
        ) {
            const marks = processedMarks;
            adjustedValue = newValue.map(val => snapToNearestMark(val, marks));
        }

        setValue(adjustedValue);
        if (updatemode === 'drag') {
            setProps({value: adjustedValue, drag_value: adjustedValue});
        } else {
            setProps({drag_value: adjustedValue});
        }
    };

    const handleValueCommit = (newValue: number[]) => {
        if (updatemode === 'mouseup') {
            setProps({value: newValue});
        }
    };

    const classNames = ['dash-slider-container', className].filter(Boolean);

    return (
        <LoadingElement>
            {loadingProps => (
                <div id={id} className={classNames.join(' ')} {...loadingProps}>
                    {showInputs && value.length === 2 && !vertical && (
                        <input
                            type="number"
                            className="dash-input-container dash-range-slider-input dash-range-slider-min-input"
                            style={{width: inputWidth}}
                            value={isNaN(value[0]) ? '' : value[0]}
                            onChange={e => {
                                const inputValue = e.target.value;

                                // Parse the input value
                                const newMin = parseFloat(inputValue);
                                const newValue = [newMin, value[1]];
                                setValue(newValue);
                                // Only update props if value is valid
                                if (valueIsValid(newMin)) {
                                    if (updatemode === 'drag') {
                                        setProps({
                                            value: newValue,
                                            drag_value: newValue,
                                        });
                                    } else {
                                        setProps({
                                            drag_value: newValue,
                                        });
                                    }
                                }
                            }}
                            onBlur={e => {
                                const inputValue = e.target.value;
                                let newMin: number;

                                // If empty, default to current value or min_mark
                                if (inputValue === '') {
                                    newMin = isNaN(value[0])
                                        ? minMaxValues.min_mark
                                        : value[0];
                                } else {
                                    newMin = parseFloat(inputValue);
                                    newMin = isNaN(newMin)
                                        ? minMaxValues.min_mark
                                        : newMin;
                                }

                                // Constrain to not exceed the max value
                                newMin = Math.min(
                                    value[1] ?? minMaxValues.max_mark,
                                    newMin
                                );

                                // Snap to valid value (respecting step and marks)
                                const constrainedMin =
                                    constrainToValidValue(newMin);
                                const newValue = [constrainedMin, value[1]];
                                setValue(newValue);
                                if (updatemode === 'mouseup') {
                                    setProps({value: newValue});
                                }
                            }}
                            pattern="^\\d*\\.?\\d*$"
                            min={minMaxValues.min_mark}
                            max={isNaN(value[1]) ? max : value[1]}
                            step={step || undefined}
                            disabled={disabled}
                        />
                    )}
                    {showInputs && !vertical && (
                        <input
                            ref={inputRef}
                            type="number"
                            className="dash-input-container dash-range-slider-input  dash-range-slider-max-input"
                            style={{width: inputWidth}}
                            value={
                                isNaN(value[value.length - 1])
                                    ? ''
                                    : value[value.length - 1]
                            }
                            onChange={e => {
                                const inputValue = e.target.value;

                                // Parse the input value
                                const newMax = parseFloat(inputValue);
                                const newValue = [...value];
                                newValue[newValue.length - 1] = newMax;
                                setValue(newValue);
                                // Only update props if value is valid
                                if (valueIsValid(newMax)) {
                                    if (updatemode === 'drag') {
                                        setProps({
                                            value: newValue,
                                            drag_value: newValue,
                                        });
                                    } else {
                                        setProps({
                                            drag_value: newValue,
                                        });
                                    }
                                }
                            }}
                            onBlur={e => {
                                const inputValue = e.target.value;
                                let newMax: number;

                                // If empty, default to current value or max_mark
                                if (inputValue === '') {
                                    newMax = isNaN(value[value.length - 1])
                                        ? minMaxValues.max_mark
                                        : value[value.length - 1];
                                } else {
                                    newMax = parseFloat(inputValue);
                                    newMax = isNaN(newMax)
                                        ? minMaxValues.max_mark
                                        : newMax;
                                }
                                // Constrain to not be less than the min value
                                newMax = Math.max(
                                    value[0] ?? minMaxValues.min_mark,
                                    newMax
                                );

                                // Snap to valid value (respecting step and marks)
                                const constrainedMax =
                                    constrainToValidValue(newMax);
                                const newValue = [...value];
                                newValue[newValue.length - 1] = constrainedMax;
                                setValue(newValue);
                                if (updatemode === 'mouseup') {
                                    setProps({value: newValue});
                                }
                            }}
                            pattern="^\\d*\\.?\\d*$"
                            min={
                                value.length === 1
                                    ? minMaxValues.min_mark
                                    : value[0]
                            }
                            max={
                                isNaN(minMaxValues.max_mark)
                                    ? max
                                    : minMaxValues.max_mark
                            }
                            step={step || undefined}
                            disabled={disabled}
                        />
                    )}
                    <div
                        className="dash-slider-wrapper"
                        onClickCapture={e => e.preventDefault()} // prevent interactions from "clicking" the parent, particularly when slider is inside a label tag
                    >
                        <RadixSlider.Root
                            ref={sliderRef}
                            className={`dash-slider-root ${
                                renderedMarks ? 'has-marks' : ''
                            }`.trim()}
                            style={{
                                ...(vertical && {
                                    height: `${verticalHeight}px`,
                                }),
                            }}
                            value={value}
                            onValueChange={handleValueChange}
                            onValueCommit={handleValueCommit}
                            min={minMaxValues.min_mark}
                            max={minMaxValues.max_mark}
                            step={stepValue}
                            disabled={disabled}
                            orientation={vertical ? 'vertical' : 'horizontal'}
                            data-included={included !== false}
                            minStepsBetweenThumbs={
                                typeof pushable === 'number'
                                    ? pushable
                                    : undefined
                            }
                        >
                            <RadixSlider.Track className="dash-slider-track">
                                {included !== false && (
                                    <RadixSlider.Range className="dash-slider-range" />
                                )}
                            </RadixSlider.Track>
                            {renderedMarks &&
                                renderSliderMarks(
                                    renderedMarks,
                                    !!vertical,
                                    minMaxValues,
                                    !!dots
                                )}
                            {dots &&
                                stepValue &&
                                renderSliderDots(
                                    stepValue,
                                    minMaxValues,
                                    !!vertical
                                )}
                            {/* Render thumbs with tooltips for each value */}
                            {value.map((val, index) => {
                                const thumbClassName = `dash-slider-thumb dash-slider-thumb-${
                                    index + 1
                                }`;

                                return (
                                    <RadixSlider.Thumb
                                        key={'thumb' + index}
                                        className={thumbClassName}
                                    >
                                        {tooltip && (
                                            <Tooltip
                                                id={id}
                                                index={index}
                                                value={val}
                                                tooltip={tooltip}
                                            />
                                        )}
                                    </RadixSlider.Thumb>
                                );
                            })}
                        </RadixSlider.Root>
                    </div>
                </div>
            )}
        </LoadingElement>
    );
}
