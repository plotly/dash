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
import {SliderProps} from '../types';

const MAX_MARKS = 500;

/**
 * A slider component with a single handle.
 */
export default function Slider(props: SliderProps) {
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
    } = props;

    // Radix UI expects arrays, so we normalize the value
    const [value, setValue] = useState<number | null>(propValue || null);

    // Track slider dimension (width for horizontal, height for vertical) for dynamic mark density
    const [sliderWidth, setSliderWidth] = useState<number | null>(null);
    const [showInput, setShowInput] = useState<boolean>(true);
    const sliderRef = useRef<HTMLDivElement>(null);

    // Convert single value to array format for Radix UI
    const radixValue = useMemo(() => {
        return value !== null ? [value] : undefined;
    }, [value]);

    // Handle initial mount - equivalent to componentWillMount
    useEffect(() => {
        if (propValue !== null && propValue !== undefined) {
            setProps({drag_value: propValue});
            setValue(propValue);
        } else {
            // No value came down, so we send the slider default value back up: the value prop will always be set after this point.
            setProps({value: min});
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

                    const HIDE_AT_WIDTH = 200;
                    const SHOW_AT_WIDTH = 300;
                    if (showInput && dimension < HIDE_AT_WIDTH) {
                        setShowInput(false);
                    } else if (!showInput && dimension >= SHOW_AT_WIDTH) {
                        setShowInput(true);
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
    }, [showInput, vertical]);

    // Handle prop value changes - equivalent to componentWillReceiveProps
    useEffect(() => {
        if (propValue !== value) {
            setProps({drag_value: propValue || undefined});
            setValue(propValue || null);
        }
    }, [propValue]);

    // Check if marks exceed 500 limit for performance
    let processedMarks = marks;
    if (marks && typeof marks === 'object' && marks !== null) {
        const marksCount = Object.keys(marks).length;
        if (marksCount > MAX_MARKS) {
            /* eslint-disable no-console */
            console.error(
                `dcc.Slider: Too many marks (${marksCount}) provided. ` +
                    `For performance reasons, marks are limited to 500. ` +
                    `Using auto-generated marks instead.`
            );
            processedMarks = undefined;
        }
    }

    // Tooltip configuration for Radix UI
    const tooltipContent = useMemo(() => {
        if (!tooltip || value === null) {
            return null;
        }

        let displayValue: number | string = value;
        if (tooltip.transform) {
            displayValue = transformSliderTooltip(tooltip.transform, value);
        }

        const content = formatSliderTooltip(
            tooltip.template || '{value}',
            displayValue
        );

        return (
            <div id={`${id}-tooltip-content`} style={tooltip.style}>
                {content}
            </div>
        );
    }, [tooltip, value]);

    const minMaxValues = useMemo(() => {
        return setUndefined(min, max, processedMarks);
    }, [min, max, processedMarks]);

    const stepValue: number | undefined = useMemo(() => {
        return step === null && !isNil(processedMarks)
            ? undefined
            : calcStep(min, max, step);
    }, [step, processedMarks, min, max]);

    // Generate marks for rendering (if needed)
    const renderedMarks = useMemo(() => {
        return sanitizeMarks({
            min,
            max,
            marks: processedMarks,
            step,
            sliderWidth,
        });
    }, [min, max, processedMarks, step, sliderWidth]);

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
                    <div className="dash-slider-wrapper">
                        <Tooltip.Provider>
                            <RadixSlider.Root
                                ref={sliderRef}
                                className={`dash-slider-root ${
                                    renderedMarks ? 'has-marks' : ''
                                } ${className || ''}`.trim()}
                                style={{
                                    position: 'relative',
                                    ...(vertical && {
                                        height: `${verticalHeight}px`,
                                    }),
                                }}
                                value={radixValue}
                                onValueChange={(newValue: number[]) => {
                                    const singleValue = newValue[0];

                                    setValue(singleValue);
                                    if (updatemode === 'drag') {
                                        setProps({
                                            value: singleValue,
                                            drag_value: singleValue,
                                        });
                                    } else {
                                        setProps({drag_value: singleValue});
                                    }
                                }}
                                onValueCommit={() => {
                                    if (updatemode === 'mouseup') {
                                        setProps({value});
                                    }
                                }}
                                min={minMaxValues.min_mark}
                                max={minMaxValues.max_mark}
                                step={stepValue}
                                disabled={disabled}
                                orientation={
                                    vertical ? 'vertical' : 'horizontal'
                                }
                                data-included={included !== false}
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
                                            const style = vertical
                                                ? {
                                                      bottom: `calc(${thumbPosition.percentage}% + ${thumbPosition.offset}px - 13px)`,
                                                      left: 'calc(100% + 8px)',
                                                      transform:
                                                          'translateY(-50%)',
                                                  }
                                                : {
                                                      left: `calc(${thumbPosition.percentage}% + ${thumbPosition.offset}px)`,
                                                      bottom: 0,
                                                      transform:
                                                          'translateX(-50%)',
                                                  };

                                            return (
                                                <div
                                                    key={position}
                                                    className="dash-slider-mark"
                                                    style={{
                                                        ...style,
                                                        ...(typeof mark ===
                                                            'object' &&
                                                        mark.style
                                                            ? mark.style
                                                            : {}),
                                                    }}
                                                >
                                                    {typeof mark === 'string'
                                                        ? mark
                                                        : mark?.label || pos}
                                                </div>
                                            );
                                        }
                                    )}

                                {/* Render dots if enabled */}
                                {dots &&
                                    stepValue &&
                                    Array.from(
                                        {
                                            length:
                                                Math.floor(
                                                    (minMaxValues.max_mark -
                                                        minMaxValues.min_mark) /
                                                        stepValue
                                                ) + 1,
                                        },
                                        (_, i) => {
                                            const dotValue =
                                                minMaxValues.min_mark +
                                                i * stepValue;
                                            const percentage =
                                                ((dotValue -
                                                    minMaxValues.min_mark) /
                                                    (minMaxValues.max_mark -
                                                        minMaxValues.min_mark)) *
                                                100;
                                            const dotStyle = vertical
                                                ? {
                                                      bottom: `${percentage}%`,
                                                      left: '50%',
                                                      transform:
                                                          'translateX(-50%)',
                                                  }
                                                : {
                                                      left: `${percentage}%`,
                                                      top: '50%',
                                                      transform:
                                                          'translateY(-50%)',
                                                  };

                                            return (
                                                <div
                                                    key={i}
                                                    className="dash-slider-dot"
                                                    style={{
                                                        position: 'absolute',
                                                        width: '8px',
                                                        height: '8px',
                                                        borderRadius: '50%',
                                                        backgroundColor: '#ddd',
                                                        ...dotStyle,
                                                    }}
                                                />
                                            );
                                        }
                                    )}

                                {/* Thumb with tooltip */}
                                {tooltip ? (
                                    <Tooltip.Root
                                        open={
                                            tooltip.always_visible || undefined
                                        }
                                    >
                                        <Tooltip.Trigger asChild>
                                            <RadixSlider.Thumb className="dash-slider-thumb" />
                                        </Tooltip.Trigger>
                                        <Tooltip.Portal>
                                            <Tooltip.Content
                                                className="dash-slider-tooltip"
                                                side={
                                                    vertical ? 'right' : 'top'
                                                }
                                                sideOffset={5}
                                            >
                                                {tooltipContent}
                                                <Tooltip.Arrow />
                                            </Tooltip.Content>
                                        </Tooltip.Portal>
                                    </Tooltip.Root>
                                ) : (
                                    <RadixSlider.Thumb className="dash-slider-thumb" />
                                )}
                            </RadixSlider.Root>
                        </Tooltip.Provider>
                    </div>
                    {showInput && !vertical && (
                        <input
                            type="number"
                            className="dash-input-container dash-slider-input"
                            value={value || ''}
                            onChange={e => {
                                setValue(parseFloat(e.target.value));
                            }}
                            onBlur={e => {
                                // Constrain value to the given min and max
                                let value = parseFloat(e.target.value) || 0;
                                value = isNaN(value) ? 0 : value;
                                const constrainedValue = Math.max(
                                    minMaxValues.min_mark,
                                    Math.min(minMaxValues.max_mark, value || 0)
                                );
                                setValue(constrainedValue);
                            }}
                            pattern="^\\d*\\.?\\d*$"
                            min={minMaxValues.min_mark}
                            max={minMaxValues.max_mark}
                            disabled={disabled}
                        />
                    )}
                </div>
            )}
        </LoadingElement>
    );
}
