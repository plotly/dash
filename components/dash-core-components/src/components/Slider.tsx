import {omit} from 'ramda';
import React, {lazy, Suspense, useCallback, useMemo} from 'react';
import {
    PersistedProps,
    PersistenceTypes,
    RangeSliderProps,
    SliderProps,
} from '../types';
import rangeSlider from '../utils/LazyLoader/rangeSlider';
import './css/sliders.css';

const RealSlider = lazy(rangeSlider);

/**
 * A slider component with a single handle.
 */
export default function Slider({
    updatemode = 'mouseup',
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persisted_props = [PersistedProps.value],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persistence_type = PersistenceTypes.local,
    // eslint-disable-next-line no-magic-numbers
    verticalHeight = 400,
    step = undefined,
    allow_direct_input = true,
    setProps,
    value,
    drag_value,
    ...props
}: SliderProps) {
    // This is actually a wrapper around a RangeSlider.
    // We'll modify key `Slider` props to be compatible with a Range Slider.

    // Some considerations for the default value of `step`:
    // If the range consists of integers, default to a value of `1`
    // Otherwise, leave it undefined
    if (
        typeof step === 'undefined' &&
        Number.isInteger(props.min) &&
        Number.isInteger(props.max)
    ) {
        step = 1;
    }

    const mappedValue: RangeSliderProps['value'] = useMemo(() => {
        return typeof value === 'number' ? [value] : value;
    }, [value]);

    const mappedDragValue: RangeSliderProps['drag_value'] = useMemo(() => {
        return typeof drag_value === 'number' ? [drag_value] : drag_value;
    }, [drag_value]);

    const mappedSetProps: RangeSliderProps['setProps'] = useCallback(
        newProps => {
            const {value, drag_value} = newProps;
            const mappedProps: Partial<SliderProps> = omit(
                ['value', 'drag_value', 'setProps'],
                newProps
            );
            if ('value' in newProps) {
                mappedProps.value = value ? value[0] : value;
            }
            if ('drag_value' in newProps) {
                mappedProps.drag_value = drag_value
                    ? drag_value[0]
                    : drag_value;
            }

            setProps(mappedProps);
        },
        [setProps]
    );

    return (
        <Suspense fallback={null}>
            <RealSlider
                updatemode={updatemode}
                verticalHeight={verticalHeight}
                step={step}
                allow_direct_input={allow_direct_input}
                value={mappedValue}
                drag_value={mappedDragValue}
                setProps={mappedSetProps}
                {...props}
            />
        </Suspense>
    );
}

Slider.dashPersistence = {
    persisted_props: [PersistedProps.value],
    persistence_type: PersistenceTypes.local,
};
