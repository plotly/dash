import {omit} from 'ramda';
import React, {lazy, Suspense, useCallback, useMemo} from 'react';
import {
    PersistedProps,
    PersistenceTypes,
    DateSliderProps,
    DateRangeSliderProps,
} from '../types';
import dateRangeSlider from '../utils/LazyLoader/dateRangeSlider';
import './css/sliders.css';

const RealSlider = lazy(dateRangeSlider);

/**
 * A slider component for selecting a single date.
 * This is a wrapper around DateRangeSlider that handles date values.
 */
export default function DateSlider({
    updatemode = 'mouseup',
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persisted_props = [PersistedProps.value],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persistence_type = PersistenceTypes.local,
    // eslint-disable-next-line no-magic-numbers
    verticalHeight = 400,
    allow_direct_input = true,
    setProps,
    value,
    drag_value,
    id,
    vertical = false,
    ...props
}: DateSliderProps) {
    // Convert single date value to array for DateRangeSlider
    const mappedValue: DateRangeSliderProps['value'] = useMemo(() => {
        return typeof value === 'string' ? [value] : value;
    }, [value]);

    // Convert single date drag value to array for DateRangeSlider
    const mappedDragValue: DateRangeSliderProps['drag_value'] = useMemo(() => {
        return typeof drag_value === 'string' ? [drag_value] : drag_value;
    }, [drag_value]);

    const mappedSetProps: DateRangeSliderProps['setProps'] = useCallback(
        newProps => {
            const {value, drag_value} = newProps;
            const mappedProps: Partial<DateSliderProps> = omit(
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
                id={id}
                updatemode={updatemode}
                verticalHeight={verticalHeight}
                allow_direct_input={allow_direct_input}
                vertical={vertical}
                value={mappedValue}
                drag_value={mappedDragValue}
                setProps={mappedSetProps}
                {...props}
            />
        </Suspense>
    );
}

DateSlider.dashPersistence = {
    persisted_props: [PersistedProps.value],
    persistence_type: PersistenceTypes.local,
};
