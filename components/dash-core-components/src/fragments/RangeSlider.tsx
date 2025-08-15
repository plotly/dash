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
    const [showInputs, setShowInputs] = useState<boolean>(true);
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
    }, [showInputs, vertical]);

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
        return step === null && !isNil(processedMarks)
            ? undefined
            : calcStep(min, max, step);
    }, [min, max, processedMarks, step]);

    // Sanitize marks for rendering
    const renderedMarks = useMemo(() => {
        return sanitizeMarks({
            min,
            max,
            marks: processedMarks,
            step,
            sliderWidth,
        });
    }, [min, max, processedMarks, step, sliderWidth]);

    const handleValueChange = (newValue: number[]) => {
        setValue(newValue);
        if (updatemode === 'drag') {
            setProps({value: newValue, drag_value: newValue});
        } else {
            setProps({drag_value: newValue});
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

    // Replicate Radix UI's exact positioning logic including pixel offsets
    const convertValueToPercentage = (
        value: number,
        min: number,
        max: number
    ) => {
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
    const getRadixThumbPosition = (value: number, thumbWidth = 16) => {
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

    return (
        <LoadingElement>
            {loadingProps => (
                <div className="dash-slider-container" {...loadingProps}>
                    {showInputs && !vertical && (
                        <input
                            type="number"
                            className="dash-input-container dash-range-slider-input dash-range-slider-min-input"
                            value={value[0] || ''}
                            onChange={e => {
                                const newMin = parseFloat(e.target.value);
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
                            }}
                            onBlur={e => {
                                let newMin =
                                    parseFloat(e.target.value) ||
                                    minMaxValues.min_mark;
                                newMin = isNaN(newMin)
                                    ? minMaxValues.min_mark
                                    : newMin;
                                const constrainedMin = Math.max(
                                    minMaxValues.min_mark,
                                    Math.min(value[1], newMin)
                                );
                                const newValue = [constrainedMin, value[1]];
                                setValue(newValue);
                                if (updatemode === 'mouseup') {
                                    setProps({value: newValue});
                                }
                            }}
                            min={minMaxValues.min_mark}
                            max={value[1]}
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
                                {/* Render marks if they exist */}
                                {renderedMarks &&
                                    Object.entries(renderedMarks).map(
                                        ([position, mark]) => {
                                            const pos = parseFloat(position);
                                            // Use the exact same positioning logic as Radix UI thumbs
                                            const thumbPosition =
                                                getRadixThumbPosition(pos);
                                            const markStyle: React.CSSProperties =
                                                vertical
                                                    ? {
                                                          bottom: `calc(${thumbPosition.percentage}% + ${thumbPosition.offset}px - 13px)`,
                                                          left: 'calc(100% + 8px)',
                                                          transform:
                                                              'translateY(-50%)',
                                                      }
                                                    : {
                                                          left: `calc(${thumbPosition.percentage}% + ${thumbPosition.offset}px)`,
                                                          bottom: 0, // Position at the bottom edge of container
                                                          transform:
                                                              'translateX(-50%)',
                                                      };

                                            const markContent =
                                                typeof mark === 'string'
                                                    ? mark
                                                    : mark.label;
                                            const markLabelStyle =
                                                typeof mark === 'object'
                                                    ? mark.style
                                                    : undefined;

                                            return (
                                                <div
                                                    key={position}
                                                    className="dash-slider-mark"
                                                    style={markStyle}
                                                >
                                                    <div className="dash-slider-mark-dot" />
                                                    {markContent && (
                                                        <div
                                                            className="dash-slider-mark-label"
                                                            style={
                                                                markLabelStyle
                                                            }
                                                        >
                                                            {markContent}
                                                        </div>
                                                    )}
                                                </div>
                                            );
                                        }
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
                            value={value[1] || ''}
                            onChange={e => {
                                const newMax = parseFloat(e.target.value);
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
                            }}
                            onBlur={e => {
                                let newMax =
                                    parseFloat(e.target.value) ||
                                    minMaxValues.max_mark;
                                newMax = isNaN(newMax)
                                    ? minMaxValues.max_mark
                                    : newMax;
                                const constrainedMax = Math.min(
                                    minMaxValues.max_mark,
                                    Math.max(value[0], newMax)
                                );
                                const newValue = [value[0], constrainedMax];
                                setValue(newValue);
                                if (updatemode === 'mouseup') {
                                    setProps({value: newValue});
                                }
                            }}
                            min={value[0]}
                            max={minMaxValues.max_mark}
                            disabled={disabled}
                        />
                    )}
                </div>
            )}
        </LoadingElement>
    );
}
