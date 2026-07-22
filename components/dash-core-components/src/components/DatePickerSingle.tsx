import React, {lazy, Suspense} from 'react';
import datePickerSingle from '../utils/LazyLoader/datePickerSingle';
import transformDate from '../utils/DatePickerPersistence';
import {
    DatePickerSingleProps,
    PersistedProps,
    PersistenceTypes,
} from '../types';

const RealDatePickerSingle = lazy(datePickerSingle);

/**
 * DatePickerSingle is a tailor made component designed for selecting
 * a single day off of a calendar.
 *
 * The DatePicker integrates well with the Python datetime module with the
 * startDate and endDate being returned in a string format suitable for
 * creating datetime objects.
 */
export default function DatePickerSingle({
    placeholder = 'Select Date',
    calendar_orientation = 'horizontal',
    is_RTL = false,
    // eslint-disable-next-line no-magic-numbers
    day_size = 34,
    with_portal = false,
    with_full_screen_portal = false,
    show_outside_days = true,
    first_day_of_week = 0,
    number_of_months_shown = 1,
    stay_open_on_select = false,
    reopen_calendar_on_clear = false,
    clearable = false,
    disabled = false,
    disabled_days = [],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persisted_props = [PersistedProps.date],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persistence_type = PersistenceTypes.local,
    ...props
}: DatePickerSingleProps) {
    return (
        <Suspense fallback={null}>
            <RealDatePickerSingle
                placeholder={placeholder}
                calendar_orientation={calendar_orientation}
                is_RTL={is_RTL}
                day_size={day_size}
                with_portal={with_portal}
                with_full_screen_portal={with_full_screen_portal}
                show_outside_days={show_outside_days}
                first_day_of_week={first_day_of_week}
                number_of_months_shown={number_of_months_shown}
                stay_open_on_select={stay_open_on_select}
                reopen_calendar_on_clear={reopen_calendar_on_clear}
                clearable={clearable}
                disabled={disabled}
                disabled_days={disabled_days}
                {...props}
            />
        </Suspense>
    );
}

DatePickerSingle.dashPersistence = {
    persisted_props: [PersistedProps.date],
    persistence_type: PersistenceTypes.local,
};

DatePickerSingle.persistenceTransforms = {
    date: transformDate,
};
