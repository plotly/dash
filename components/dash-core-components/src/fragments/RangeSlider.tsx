import React, {useEffect, useState, useMemo, useRef} from 'react';
import * as RadixSlider from '@radix-ui/react-slider';
import * as Tooltip from '@radix-ui/react-tooltip';
import {isNil} from 'ramda';

import {
    sanitizeMarks,
    calcStep,
    setUndefined,
} from '../utils/computeSliderMarkers';
import {
    formatSliderTooltip,
    transformSliderTooltip,
} from '../utils/formatSliderTooltip';
import {snapToNearestMark} from '../utils/sliderSnapToMark';
import {renderSliderMarks, renderSliderDots} from '../utils/sliderRendering';
import LoadingElement from '../utils/_LoadingElement';
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
        min = 0,
        max = 100,
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
    const [value, setValue] = useState<number[]>(propValue || [min, max]);

    // Track slider dimension (width for horizontal, height for vertical) for conditional input rendering
    const [sliderWidth, setSliderWidth] = useState<number | null>(null);
    const [showInputs, setShowInputs] = useState<boolean>(value.length === 2);
    const sliderRef = useRef<HTMLDivElement>(null);

    // Handle initial mount - equivalent to componentWillMount
    useEffect(() => {
        if (propValue && propValue.length > 0) {
            setProps({drag_value: propValue});
            setValue(propValue);
        } else {
            // Default to range from min to max if no value provided
            const defaultValue = [min, max];
            setProps({drag_value: defaultValue});
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

        if (value.length !== 2) {
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

                    const HIDE_AT_WIDTH = 250;
                    const SHOW_AT_WIDTH = 450;
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
    if (marks && Object.keys(marks).length > MAX_MARKS) {
        /* eslint-disable no-console */
        console.warn(
            `RangeSlider marks exceed ${MAX_MARKS} limit for performance. Marks have been disabled.`
        );
        processedMarks = undefined;
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

    const handleValueChange = (newValue: number[]) => {
        let adjustedValue = newValue;

        // Snap to nearest marks if step is null and marks exist
        if (
            step === null &&
            processedMarks &&
            typeof processedMarks === 'object'
        ) {
            adjustedValue = newValue.map(val =>
                snapToNearestMark(val, processedMarks)
            );
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

    // Format tooltip content
    const formatTooltipContent = (value: number, index: number) => {
        let displayValue: string | number = value;
        if (tooltip?.transform) {
            displayValue = transformSliderTooltip(tooltip.transform, value);
        }
        return (
            <div
                id={`${id}-tooltip-${index + 1}-content`}
                style={tooltip?.style}
            >
                {formatSliderTooltip(
                    tooltip?.template || '{value}',
                    displayValue
                )}
            </div>
        );
    };

    return (
        <LoadingElement>
            {loadingProps => (
                <div
                    id={id}
                    className="dash-slider-container"
                    {...loadingProps}
                >
                    {showInputs && !vertical && (
                        <input
                            type="number"
                            className="dash-input-container dash-range-slider-input dash-range-slider-min-input"
                            value={value[0] ?? ''}
                            onChange={e => {
                                const inputValue = e.target.value;
                                // Allow empty string (user is clearing the field)
                                if (inputValue === '') {
                                    // Don't update props while user is typing, just update local state
                                    setValue([null as any, value[1]]);
                                } else {
                                    const newMin = parseFloat(inputValue);
                                    if (!isNaN(newMin)) {
                                        const newValue = [newMin, value[1]];
                                        setValue(newValue);
                                        if (updatemode === 'drag') {
                                            setProps({
                                                value: newValue,
                                                drag_value: newValue,
                                            });
                                        } else {
                                            setProps({drag_value: newValue});
                                        }
                                    }
                                }
                            }}
                            onBlur={e => {
                                const inputValue = e.target.value;
                                let newMin: number;

                                // If empty, default to current value or min_mark
                                if (inputValue === '') {
                                    newMin = value[0] ?? minMaxValues.min_mark;
                                } else {
                                    newMin = parseFloat(inputValue);
                                    newMin = isNaN(newMin)
                                        ? minMaxValues.min_mark
                                        : newMin;
                                }

                                const constrainedMin = Math.max(
                                    minMaxValues.min_mark,
                                    Math.min(
                                        value[1] ?? minMaxValues.max_mark,
                                        newMin
                                    )
                                );
                                const newValue = [constrainedMin, value[1]];
                                setValue(newValue);
                                if (updatemode === 'mouseup') {
                                    setProps({value: newValue});
                                }
                            }}
                            min={minMaxValues.min_mark}
                            max={value[1]}
                            step={step || undefined}
                            disabled={disabled}
                        />
                    )}
                    <div className="dash-slider-wrapper">
                        <Tooltip.Provider>
                            <RadixSlider.Root
                                ref={sliderRef}
                                className={`dash-slider-root dash-range-slider-root ${
                                    renderedMarks ? 'has-marks' : ''
                                } ${className || ''}`.trim()}
                                style={{
                                    position: 'relative',
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
                                orientation={
                                    vertical ? 'vertical' : 'horizontal'
                                }
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

                                    return tooltip ? (
                                        <Tooltip.Root
                                            key={index}
                                            open={
                                                tooltip.always_visible ||
                                                undefined
                                            }
                                        >
                                            <Tooltip.Trigger asChild>
                                                <RadixSlider.Thumb
                                                    className={thumbClassName}
                                                />
                                            </Tooltip.Trigger>
                                            <Tooltip.Portal>
                                                <Tooltip.Content
                                                    className="dash-slider-tooltip"
                                                    side={
                                                        vertical
                                                            ? 'right'
                                                            : 'top'
                                                    }
                                                    align="center"
                                                >
                                                    {formatTooltipContent(
                                                        val,
                                                        index
                                                    )}
                                                    <Tooltip.Arrow />
                                                </Tooltip.Content>
                                            </Tooltip.Portal>
                                        </Tooltip.Root>
                                    ) : (
                                        <RadixSlider.Thumb
                                            key={index}
                                            className={thumbClassName}
                                        />
                                    );
                                })}
                            </RadixSlider.Root>
                        </Tooltip.Provider>
                    </div>
                    {showInputs && !vertical && (
                        <input
                            type="number"
                            className="dash-input-container dash-range-slider-input"
                            value={value[1] ?? ''}
                            onChange={e => {
                                const inputValue = e.target.value;
                                // Allow empty string (user is clearing the field)
                                if (inputValue === '') {
                                    // Don't update props while user is typing, just update local state
                                    setValue([value[0], null as any]);
                                } else {
                                    const newMax = parseFloat(inputValue);
                                    if (!isNaN(newMax)) {
                                        const newValue = [value[0], newMax];
                                        setValue(newValue);
                                        if (updatemode === 'drag') {
                                            setProps({
                                                value: newValue,
                                                drag_value: newValue,
                                            });
                                        } else {
                                            setProps({drag_value: newValue});
                                        }
                                    }
                                }
                            }}
                            onBlur={e => {
                                const inputValue = e.target.value;
                                let newMax: number;

                                // If empty, default to current value or max_mark
                                if (inputValue === '') {
                                    newMax = value[1] ?? minMaxValues.max_mark;
                                } else {
                                    newMax = parseFloat(inputValue);
                                    newMax = isNaN(newMax)
                                        ? minMaxValues.max_mark
                                        : newMax;
                                }

                                const constrainedMax = Math.min(
                                    minMaxValues.max_mark,
                                    Math.max(
                                        value[0] ?? minMaxValues.min_mark,
                                        newMax
                                    )
                                );
                                const newValue = [value[0], constrainedMax];
                                setValue(newValue);
                                if (updatemode === 'mouseup') {
                                    setProps({value: newValue});
                                }
                            }}
                            min={value[0]}
                            max={minMaxValues.max_mark}
                            step={step || undefined}
                            disabled={disabled}
                        />
                    )}
                </div>
            )}
        </LoadingElement>
    );
}
