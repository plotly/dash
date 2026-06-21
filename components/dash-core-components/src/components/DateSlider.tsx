import React, {
    lazy,
    Suspense,
    useCallback,
    useMemo,
    useRef,
    useState,
} from 'react';
import {omit} from 'ramda';
import DatePickerSingle from '../components/DatePickerSingle';
import {
    PersistedProps,
    PersistenceTypes,
    DateSliderProps,
    DateRangeSliderProps,
} from '../types';
import {
    strAsDate,
    snapToValidDate,
    dateAsStr,
    snapToStep,
} from '../utils/calendar/helpers';
import dateRangeSlider from '../utils/LazyLoader/dateRangeSlider';
import './css/datesliders.css';

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
    min,
    max,
    display_format,
    ...props
}: DateSliderProps) {
    const [resetKey, setResetKey] = useState(0);
    const containerRef = useRef<HTMLDivElement>(null);

    // Convert single date value to array for DateRangeSlider
    const mappedValue: DateRangeSliderProps['value'] = useMemo(() => {
        return value ? [value] : value;
    }, [value]);

    // Convert single date drag value to array for DateRangeSlider
    const mappedDragValue: DateRangeSliderProps['drag_value'] = useMemo(() => {
        return drag_value ? [drag_value] : undefined;
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

    const handleDateInputChange = useCallback(
        (dateStr: `${string}-${string}-${string}` | undefined) => {
            if (!dateStr) {
                setProps({
                    value:
                        (min as `${string}-${string}-${string}`) ?? undefined,
                });
                return;
            }

            const inputDate = strAsDate(dateStr);
            if (inputDate && props.step && props.step_unit) {
                const parsedMin = strAsDate(min);
                const snapped = snapToStep(
                    inputDate,
                    parsedMin ?? inputDate,
                    props.step,
                    props.step_unit
                );
                if (snapped.getTime() !== inputDate.getTime()) {
                    setResetKey(k => k + 1); // rejeitar
                    return;
                }
            }

            const hasNoChange = value === dateStr;
            if (hasNoChange) {
                setResetKey(k => k + 1);
            } else {
                setProps({value: dateStr});
            }
        },
        [value, setProps, min, props.step, props.step_unit]
    );

    return (
        <div
            ref={containerRef}
            className="date-slider-container"
            data-vertical={vertical}
        >
            <div className="dash-slider-wrapper">
                <Suspense fallback={null}>
                    <RealSlider
                        key={resetKey}
                        id={id}
                        updatemode={updatemode}
                        verticalHeight={verticalHeight}
                        allow_direct_input={false}
                        vertical={vertical}
                        min={min}
                        max={max}
                        display_format={display_format}
                        value={mappedValue}
                        drag_value={mappedDragValue}
                        setProps={mappedSetProps}
                        {...props}
                    />
                </Suspense>
            </div>
            {allow_direct_input && (
                <div className="dash-range-slider-min-input">
                    <DatePickerSingle
                        key={`date-input-${resetKey}`}
                        date={value ?? undefined}
                        setProps={({date}) => handleDateInputChange(date)}
                        min_date_allowed={min}
                        max_date_allowed={max}
                        display_format={display_format}
                    />
                </div>
            )}
        </div>
    );
}

DateSlider.dashPersistence = {
    persisted_props: [PersistedProps.value],
    persistence_type: PersistenceTypes.local,
};
