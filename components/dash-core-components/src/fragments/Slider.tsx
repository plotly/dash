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
        return value !== null ? [value] : [NaN];
    }, [value]);

    useEffect(() => {
        if (propValue !== null && propValue !== undefined) {
            setProps({drag_value: propValue});
            setValue(propValue);
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
            setShowInput(false);
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
    }, [showInput, vertical, step]);

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
        return step === null && isNil(processedMarks)
            ? undefined
            : calcStep(min, max, step);
    }, [step, processedMarks, min, max]);

    // Generate marks for rendering (if needed)
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

    return (
        <LoadingElement>
            {loadingProps => (
                <div
                    id={id}
                    className="dash-slider-container"
                    {...loadingProps}
                >
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
                                    let singleValue = newValue[0];

                                    // Snap to nearest mark if step is null and marks exist
                                    if (
                                        step === null &&
                                        processedMarks &&
                                        typeof processedMarks === 'object'
                                    ) {
                                        singleValue = snapToNearestMark(
                                            singleValue,
                                            processedMarks
                                        );
                                    }

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
                            value={value ?? ''}
                            onChange={e => {
                                const inputValue = e.target.value;
                                // Allow empty string (user is clearing the field)
                                if (inputValue === '') {
                                    setValue(null);
                                } else {
                                    const numericValue = parseFloat(inputValue);
                                    if (!isNaN(numericValue)) {
                                        setValue(numericValue);
                                    }
                                }
                            }}
                            onBlur={e => {
                                const inputValue = e.target.value;
                                // If empty, use the current slider value or default to min
                                if (inputValue === '') {
                                    const defaultValue =
                                        value ?? minMaxValues.min_mark;
                                    setValue(defaultValue);
                                    return;
                                }

                                // Otherwise, constrain value to the given min and max
                                let numericValue = parseFloat(inputValue);
                                numericValue = isNaN(numericValue)
                                    ? minMaxValues.min_mark
                                    : numericValue;
                                const constrainedValue = Math.max(
                                    minMaxValues.min_mark,
                                    Math.min(
                                        minMaxValues.max_mark,
                                        numericValue
                                    )
                                );
                                setValue(constrainedValue);
                            }}
                            pattern="^\\d*\\.?\\d*$"
                            min={minMaxValues.min_mark}
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
