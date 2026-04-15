import React, {lazy, Suspense} from 'react';
import datePickerRange from '../utils/LazyLoader/datePickerRange';
import transformDate from '../utils/DatePickerPersistence';
import {DatePickerRangeProps, PersistedProps, PersistenceTypes} from '../types';

const RealDatePickerRange = lazy(datePickerRange);

/**
 * DatePickerRange is designed for selecting a timespan across multiple days off
 * of a calendar.
 *
 * The DatePicker integrates well with the Python datetime module with the
 * startDate and endDate being returned in a string format suitable for
 * creating datetime objects.
 *
 */
export default function DatePickerRange({
    calendar_orientation = 'horizontal',
    is_RTL = false,
    // eslint-disable-next-line no-magic-numbers
    day_size = 34,
    with_portal = false,
    with_full_screen_portal = false,
    first_day_of_week = 0,
    number_of_months_shown = 2,
    stay_open_on_select = false,
    reopen_calendar_on_clear = false,
    show_outside_days = false,
    clearable = false,
    disabled = false,
    updatemode = 'singledate',
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persisted_props = [PersistedProps.start_date, PersistedProps.end_date],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persistence_type = PersistenceTypes.local,
    disabled_days = [],
    ...props
}: DatePickerRangeProps) {
    return (
        <Suspense fallback={null}>
            <RealDatePickerRange
                calendar_orientation={calendar_orientation}
                is_RTL={is_RTL}
                day_size={day_size}
                show_outside_days={show_outside_days}
                with_portal={with_portal}
                with_full_screen_portal={with_full_screen_portal}
                first_day_of_week={first_day_of_week}
                number_of_months_shown={number_of_months_shown}
                stay_open_on_select={stay_open_on_select}
                reopen_calendar_on_clear={reopen_calendar_on_clear}
                clearable={clearable}
                disabled={disabled}
                disabled_days={disabled_days}
                updatemode={updatemode}
                {...props}
            />
        </Suspense>
    );
}

DatePickerRange.dashPersistence = {
    persisted_props: [PersistedProps.start_date, PersistedProps.end_date],
    persistence_type: PersistenceTypes.local,
};

DatePickerRange.persistenceTransforms = {
    end_date: transformDate,
    start_date: transformDate,
};
