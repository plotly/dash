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

type SliderInteractionKind = 'keyboard' | 'pointer';

interface SliderInteraction {
    kind: SliderInteractionKind;
    thumbIndex: number | null;
    startValue: number[];
}

type InputSide = 'max' | 'min';

interface InputEdit {
    side: InputSide;
    text: string;
    startValue: number[];
    fixedValue?: number;
    lastValidCandidate: number;
}

interface ThumbValueChange {
    candidate: number;
    previousIndex: number;
}

const numbersEqual = (left: number, right: number): boolean =>
    Object.is(left, right);

const valuesEqual = (left: number[], right: number[]): boolean =>
    left.length === right.length &&
    left.every((item, index) => numbersEqual(item, right[index]));

const canonicalizeValues = (values: number[]): number[] =>
    [...values].sort((left, right) => left - right);

const findThumbValueChange = (
    previousValue: number[],
    attemptedValue: number[]
): ThumbValueChange | undefined => {
    const unmatchedPrevious = previousValue.map((value, index) => ({
        index,
        value,
    }));
    let candidate: number | undefined;

    for (const attemptedCandidate of attemptedValue) {
        const matchIndex = unmatchedPrevious.findIndex(previous =>
            numbersEqual(previous.value, attemptedCandidate)
        );

        if (matchIndex === -1) {
            if (candidate !== undefined) {
                return undefined;
            }
            candidate = attemptedCandidate;
        } else {
            unmatchedPrevious.splice(matchIndex, 1);
        }
    }

    return candidate !== undefined && unmatchedPrevious.length === 1
        ? {
              candidate,
              previousIndex: unmatchedPrevious[0].index,
          }
        : undefined;
};

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
        allowCross = true,
        pushable,
        count,
        reverse,
        allow_direct_input = true,
    } = props;

    // For range slider, we expect an array of values
    const [value, setValue] = useState<number[]>(
        propValue ? [...propValue] : []
    );
    const [inputEdit, setInputEdit] = useState<InputEdit | null>(null);

    // Track slider dimension (width for horizontal, height for vertical) for marks rendering
    const [sliderWidth, setSliderWidth] = useState<number | null>(null);

    const sliderRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const valueRef = useRef<number[]>(value);
    const inputEditRef = useRef<InputEdit | null>(null);
    const interactionRef = useRef<SliderInteraction | null>(null);
    const thumbRefs = useRef<Array<HTMLSpanElement | null>>([]);
    const pendingValueEchoRef = useRef<number[] | null>(null);

    const setSliderProps = (newProps: Partial<RangeSliderProps>) => {
        if (Array.isArray(newProps.value)) {
            pendingValueEchoRef.current = [...newProps.value];
        }
        setProps(newProps);
    };

    // Handle initial mount - equivalent to componentWillMount
    useEffect(() => {
        if (propValue && propValue.length > 0) {
            const initialValue = [...propValue];
            setSliderProps({drag_value: initialValue});
            valueRef.current = initialValue;
            setValue(initialValue);
        } else {
            // Default to range from min to max if no value provided
            const defaultValue = [min ?? (propValue ? propValue[0] : 0)];
            valueRef.current = defaultValue;
            setValue(defaultValue);
        }
    }, []);

    // Dynamic dimension detection using ResizeObserver for marks rendering
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
    }, [vertical]);

    // Handle prop value changes - equivalent to componentWillReceiveProps
    useEffect(() => {
        if (propValue) {
            const incomingValue = [...propValue];
            const pendingValueEcho = pendingValueEchoRef.current;
            const isLocalValueEcho =
                pendingValueEcho !== null &&
                valuesEqual(incomingValue, pendingValueEcho);
            pendingValueEchoRef.current = null;

            if (!isLocalValueEcho) {
                if (inputEditRef.current) {
                    inputEditRef.current = null;
                    setInputEdit(null);
                }

                const currentInteraction = interactionRef.current;
                if (currentInteraction) {
                    if (
                        currentInteraction.kind === 'keyboard' &&
                        currentInteraction.startValue.length !==
                            incomingValue.length
                    ) {
                        interactionRef.current = null;
                    } else {
                        currentInteraction.startValue = [...incomingValue];
                        if (
                            currentInteraction.thumbIndex !== null &&
                            currentInteraction.thumbIndex >=
                                incomingValue.length
                        ) {
                            currentInteraction.thumbIndex = null;
                        }
                    }
                }
            }

            if (!valuesEqual(incomingValue, valueRef.current)) {
                setSliderProps({drag_value: incomingValue});
                valueRef.current = incomingValue;
                setValue(incomingValue);
            }
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

    // Calculate dynamic input width based on min/max values
    const inputWidth = useMemo(() => {
        const maxIntegerChars = Math.max(
            String(Math.floor(minMaxValues.max_mark)).length,
            String(Math.floor(minMaxValues.min_mark)).length
        );

        const maxDecimalChars = Math.min(
            (String(stepValue).split('.')[1]?.length ?? -1) + 1,
            3
        );

        const totalChars = maxIntegerChars + maxDecimalChars;

        return `calc(${totalChars}ch + calc(var(--Dash-Spacing) * 2))`;
    }, [minMaxValues.min_mark, minMaxValues.max_mark, stepValue]);

    const valueIsValid = (val: number): boolean => {
        if (!Number.isFinite(val)) {
            return false;
        }

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

    const isKeyboardControlKey = (key: string): boolean =>
        [
            'ArrowDown',
            'ArrowLeft',
            'ArrowRight',
            'ArrowUp',
            'End',
            'Home',
            'PageDown',
            'PageUp',
        ].includes(key);

    const updateInputEdit = (edit: InputEdit | null) => {
        inputEditRef.current = edit;
        setInputEdit(edit);
    };

    const updateCurrentValue = (newValue: number[]): boolean => {
        const canonicalValue = canonicalizeValues(newValue);

        if (valuesEqual(canonicalValue, valueRef.current)) {
            return false;
        }

        valueRef.current = canonicalValue;
        setValue(canonicalValue);
        return true;
    };

    const publishValueChange = (newValue: number[]) => {
        const canonicalValue = canonicalizeValues(newValue);

        if (!updateCurrentValue(canonicalValue)) {
            return;
        }

        if (updatemode === 'drag') {
            setSliderProps({
                value: canonicalValue,
                drag_value: canonicalValue,
            });
        } else {
            setSliderProps({drag_value: canonicalValue});
        }
    };

    const commitSliderInteraction = (interaction: SliderInteraction) => {
        if (
            updatemode === 'mouseup' &&
            !valuesEqual(valueRef.current, interaction.startValue)
        ) {
            setSliderProps({value: [...valueRef.current]});
        }
    };

    const startSliderInteraction = (
        kind: SliderInteractionKind,
        thumbIndex: number | null
    ) => {
        const currentInteraction = interactionRef.current;

        if (currentInteraction) {
            if (currentInteraction.thumbIndex === null && thumbIndex !== null) {
                currentInteraction.thumbIndex = thumbIndex;
            }

            if (currentInteraction.kind === kind) {
                return;
            }

            // Keep a captured pointer gesture authoritative until release.
            // If a pointer starts during a keyboard gesture, commit the
            // keyboard value before starting the new pointer transaction.
            if (currentInteraction.kind === 'pointer') {
                return;
            }

            interactionRef.current = null;
            commitSliderInteraction(currentInteraction);
        }

        interactionRef.current = {
            kind,
            thumbIndex,
            startValue: [...valueRef.current],
        };
    };

    const finishSliderInteraction = (kind: SliderInteractionKind) => {
        const currentInteraction = interactionRef.current;

        if (!currentInteraction || currentInteraction.kind !== kind) {
            return;
        }

        interactionRef.current = null;
        commitSliderInteraction(currentInteraction);
    };

    const findClosestThumbFromPointer = (
        event: React.PointerEvent<HTMLElement>
    ): number | null => {
        const currentValue = valueRef.current;
        if (currentValue.length === 0) {
            return null;
        }

        const bounds = event.currentTarget.getBoundingClientRect();
        const dimension = vertical ? bounds.height : bounds.width;
        if (dimension <= 0) {
            return null;
        }

        const pointerOffset = vertical
            ? event.clientY - bounds.top
            : event.clientX - bounds.left;
        const pointerRatio = pointerOffset / dimension;
        const valuesIncreaseFromStart = vertical ? !!reverse : !reverse;
        const valueRatio = valuesIncreaseFromStart
            ? pointerRatio
            : 1 - pointerRatio;
        const pointerValue =
            minMaxValues.min_mark +
            valueRatio * (minMaxValues.max_mark - minMaxValues.min_mark);

        let closestIndex = 0;
        let closestDistance = Math.abs(currentValue[0] - pointerValue);
        for (let index = 1; index < currentValue.length; index++) {
            const distance = Math.abs(currentValue[index] - pointerValue);
            if (distance < closestDistance) {
                closestIndex = index;
                closestDistance = distance;
            }
        }

        return closestIndex;
    };

    const buildValueForThumbCandidate = (
        activeThumbIndex: number,
        candidate: number
    ): number[] => {
        const previousValue = valueRef.current;

        if (allowCross) {
            const taggedValues = previousValue.map((item, index) => ({
                originalIndex: index,
                value: index === activeThumbIndex ? candidate : item,
            }));
            taggedValues.sort(
                (left, right) =>
                    left.value - right.value ||
                    left.originalIndex - right.originalIndex
            );

            const currentInteraction = interactionRef.current;
            if (currentInteraction) {
                currentInteraction.thumbIndex = taggedValues.findIndex(
                    item => item.originalIndex === activeThumbIndex
                );
            }

            return taggedValues.map(item => item.value);
        }

        const nextValue = [...previousValue];
        const lowerBound =
            activeThumbIndex > 0
                ? previousValue[activeThumbIndex - 1]
                : minMaxValues.min_mark;
        const upperBound =
            activeThumbIndex < previousValue.length - 1
                ? previousValue[activeThumbIndex + 1]
                : minMaxValues.max_mark;
        nextValue[activeThumbIndex] = Math.max(
            lowerBound,
            Math.min(upperBound, candidate)
        );
        return nextValue;
    };

    const deriveValueFromAttempt = (attemptedValue: number[]): number[] => {
        const previousValue = valueRef.current;
        const currentInteraction = interactionRef.current;

        if (!currentInteraction) {
            return canonicalizeValues(attemptedValue);
        }

        const valueChange = findThumbValueChange(previousValue, attemptedValue);
        if (!valueChange) {
            return previousValue;
        }

        const activeThumbIndex =
            currentInteraction.thumbIndex ?? valueChange.previousIndex;
        currentInteraction.thumbIndex = activeThumbIndex;
        if (
            activeThumbIndex >= attemptedValue.length ||
            activeThumbIndex >= previousValue.length
        ) {
            return canonicalizeValues(attemptedValue);
        }

        let {candidate} = valueChange;
        if (
            step === null &&
            processedMarks &&
            typeof processedMarks === 'object'
        ) {
            candidate = snapToNearestMark(candidate, processedMarks);
        }

        return buildValueForThumbCandidate(activeThumbIndex, candidate);
    };

    const handleValueChange = (attemptedValue: number[]) => {
        const adjustedValue = deriveValueFromAttempt(attemptedValue);
        publishValueChange(adjustedValue);

        const currentInteraction = interactionRef.current;
        if (currentInteraction && currentInteraction.thumbIndex !== null) {
            const activeThumb =
                thumbRefs.current[currentInteraction.thumbIndex];

            if (activeThumb && document.activeElement !== activeThumb) {
                activeThumb.focus();
            }
        }
    };

    const createInputEdit = (side: InputSide, text?: string): InputEdit => {
        const currentValue = valueRef.current;
        const activeIndex = side === 'min' ? 0 : currentValue.length - 1;
        const activeValue =
            currentValue[activeIndex] ??
            (side === 'min' ? minMaxValues.min_mark : minMaxValues.max_mark);

        return {
            side,
            text: text ?? String(activeValue),
            startValue: [...currentValue],
            fixedValue:
                currentValue.length === 2
                    ? currentValue[side === 'min' ? 1 : 0]
                    : undefined,
            lastValidCandidate: activeValue,
        };
    };

    const beginInputEdit = (side: InputSide) => {
        if (inputEditRef.current?.side !== side) {
            updateInputEdit(createInputEdit(side));
        }
    };

    const buildDirectInputValue = (
        edit: InputEdit,
        candidate: number
    ): number[] => {
        if (edit.fixedValue === undefined) {
            return [candidate];
        }

        if (allowCross) {
            return canonicalizeValues([candidate, edit.fixedValue]);
        }

        return edit.side === 'min'
            ? [Math.min(candidate, edit.fixedValue), edit.fixedValue]
            : [edit.fixedValue, Math.max(candidate, edit.fixedValue)];
    };

    const handleInputChange = (side: InputSide, text: string) => {
        const currentEdit =
            inputEditRef.current?.side === side
                ? inputEditRef.current
                : createInputEdit(side, text);
        const candidate = parseFloat(text);
        const nextEdit = {
            ...currentEdit,
            text,
            lastValidCandidate: valueIsValid(candidate)
                ? candidate
                : currentEdit.lastValidCandidate,
        };
        updateInputEdit(nextEdit);

        if (valueIsValid(candidate)) {
            publishValueChange(buildDirectInputValue(nextEdit, candidate));
        }
    };

    const finishInputEdit = (side: InputSide) => {
        const currentEdit = inputEditRef.current;

        if (!currentEdit || currentEdit.side !== side) {
            return;
        }

        const parsedCandidate = parseFloat(currentEdit.text);
        const candidate = constrainToValidValue(
            Number.isFinite(parsedCandidate)
                ? parsedCandidate
                : currentEdit.lastValidCandidate
        );
        const finalValue = buildDirectInputValue(currentEdit, candidate);
        const currentValueChanged = updateCurrentValue(finalValue);

        if (updatemode === 'drag') {
            if (currentValueChanged) {
                setSliderProps({
                    value: finalValue,
                    drag_value: finalValue,
                });
            }
        } else {
            const propsToPublish: Partial<RangeSliderProps> = {};

            if (!valuesEqual(finalValue, currentEdit.startValue)) {
                propsToPublish.value = finalValue;
            }
            if (currentValueChanged) {
                propsToPublish.drag_value = finalValue;
            }
            if (
                propsToPublish.value !== undefined ||
                propsToPublish.drag_value !== undefined
            ) {
                setSliderProps(propsToPublish);
            }
        }

        updateInputEdit(null);
    };

    const inputDisplayValue = (side: InputSide): string | number => {
        if (inputEdit) {
            if (inputEdit.side === side) {
                return inputEdit.text;
            }

            if (inputEdit.fixedValue !== undefined) {
                return inputEdit.fixedValue;
            }
        }

        const valueIndex = side === 'min' ? 0 : value.length - 1;
        return isNaN(value[valueIndex]) ? '' : value[valueIndex];
    };

    const classNames = ['dash-slider-container', className].filter(Boolean);

    // Determine if inputs should be rendered at all (CSS will handle responsive visibility)
    const shouldShowInputs =
        allow_direct_input !== false && // Not disabled by allow_direct_input
        step !== null && // Not disabled by step=None
        value.length <= 2 && // Only for single or range sliders
        !vertical; // Only for horizontal sliders

    return (
        <LoadingElement>
            {loadingProps => (
                <div id={id} className={classNames.join(' ')} {...loadingProps}>
                    {shouldShowInputs && value.length === 2 && (
                        <input
                            type="number"
                            className="dash-input-container dash-range-slider-input dash-range-slider-min-input"
                            style={{width: inputWidth}}
                            value={inputDisplayValue('min')}
                            onFocus={() => beginInputEdit('min')}
                            onChange={e =>
                                handleInputChange('min', e.currentTarget.value)
                            }
                            onBlur={() => finishInputEdit('min')}
                            pattern="^\\d*\\.?\\d*$"
                            min={minMaxValues.min_mark}
                            max={allowCross || isNaN(value[1]) ? max : value[1]}
                            step={step || undefined}
                            disabled={disabled}
                        />
                    )}
                    {shouldShowInputs && (
                        <input
                            ref={inputRef}
                            type="number"
                            className="dash-input-container dash-range-slider-input  dash-range-slider-max-input"
                            style={{width: inputWidth}}
                            value={inputDisplayValue('max')}
                            onFocus={() => beginInputEdit('max')}
                            onChange={e =>
                                handleInputChange('max', e.currentTarget.value)
                            }
                            onBlur={() => finishInputEdit('max')}
                            pattern="^\\d*\\.?\\d*$"
                            min={
                                allowCross || value.length === 1
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
                            onPointerDown={event =>
                                startSliderInteraction(
                                    'pointer',
                                    findClosestThumbFromPointer(event)
                                )
                            }
                            onPointerUp={() =>
                                finishSliderInteraction('pointer')
                            }
                            onPointerCancel={() =>
                                finishSliderInteraction('pointer')
                            }
                            onLostPointerCapture={() =>
                                finishSliderInteraction('pointer')
                            }
                            onKeyUp={e => {
                                if (isKeyboardControlKey(e.key)) {
                                    finishSliderInteraction('keyboard');
                                }
                            }}
                            min={minMaxValues.min_mark}
                            max={minMaxValues.max_mark}
                            step={stepValue}
                            disabled={disabled}
                            orientation={vertical ? 'vertical' : 'horizontal'}
                            inverted={reverse}
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
                                    value,
                                    !!dots,
                                    !!reverse
                                )}
                            {dots &&
                                stepValue &&
                                renderSliderDots(
                                    stepValue,
                                    minMaxValues,
                                    value,
                                    !!vertical,
                                    !!reverse
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
                                        ref={thumb => {
                                            thumbRefs.current[index] = thumb;
                                        }}
                                        onPointerDown={() => {
                                            startSliderInteraction(
                                                'pointer',
                                                index
                                            );
                                        }}
                                        onKeyDown={e => {
                                            if (
                                                !disabled &&
                                                isKeyboardControlKey(e.key)
                                            ) {
                                                startSliderInteraction(
                                                    'keyboard',
                                                    index
                                                );
                                                if (
                                                    e.key === 'Home' ||
                                                    e.key === 'End'
                                                ) {
                                                    e.preventDefault();
                                                    publishValueChange(
                                                        buildValueForThumbCandidate(
                                                            index,
                                                            e.key === 'Home'
                                                                ? constrainToValidValue(
                                                                      minMaxValues.min_mark
                                                                  )
                                                                : constrainToValidValue(
                                                                      minMaxValues.max_mark
                                                                  )
                                                        )
                                                    );
                                                    const destinationIndex =
                                                        interactionRef.current
                                                            ?.thumbIndex;
                                                    if (
                                                        destinationIndex !==
                                                            null &&
                                                        destinationIndex !==
                                                            undefined &&
                                                        destinationIndex !==
                                                            index
                                                    ) {
                                                        thumbRefs.current[
                                                            destinationIndex
                                                        ]?.focus();
                                                    }
                                                }
                                            }
                                        }}
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
