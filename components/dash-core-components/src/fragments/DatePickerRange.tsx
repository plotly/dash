import React from 'react';
import Calendar from '../utils/calendar/Calendar';
import {DatePickerRangeProps, CalendarDirection} from '../types';
import {dateAsStr, strAsDate} from '../utils/calendar/helpers';
import '../components/css/datepickers.css';

const DatePickerRange = ({
    start_date,
    end_date,
    first_day_of_week,
    show_outside_days,
    is_RTL = false,
    setProps,
}: DatePickerRangeProps) => {
    // Convert boolean is_RTL to CalendarDirection enum
    const direction = is_RTL ? CalendarDirection.RightToLeft : CalendarDirection.LeftToRight;
    
    const startDate = strAsDate(start_date);
    const endDate = strAsDate(end_date);

    // Helper to ensure dates are always sorted (start before end)
    const sortDates = (newStart?: Date, newEnd?: Date) => {
        // If both undefined or only one defined, return single date as start
        if (!newStart || !newEnd) {
            const singleDate = newStart || newEnd;
            return {
                start_date: singleDate ? dateAsStr(singleDate) : undefined,
                end_date: undefined,
            };
        }

        // Both defined - ensure proper order
        const [start, end] =
            newStart <= newEnd ? [newStart, newEnd] : [newEnd, newStart];
        return {
            start_date: dateAsStr(start),
            end_date: dateAsStr(end),
        };
    };

    return (
        <div className="dash-datepicker dash-date-picker-range">
            <Calendar
                initialVisibleDate={startDate}
                selectionStart={startDate}
                highlightStart={startDate}
                highlightEnd={endDate}
                maxDateAllowed={endDate}
                onSelectionChange={selection => {
                    setProps(sortDates(selection, endDate));
                }}
                firstDayOfWeek={first_day_of_week}
                showOutsideDays={show_outside_days}
                direction={direction}
            />
            <Calendar
                initialVisibleDate={endDate || startDate}
                selectionEnd={endDate}
                highlightStart={startDate}
                highlightEnd={endDate}
                minDateAllowed={startDate}
                onSelectionChange={selection => {
                    setProps(sortDates(startDate, selection));
                }}
                firstDayOfWeek={first_day_of_week}
                showOutsideDays={show_outside_days}
                direction={direction}
            />
        </div>
    );
};

export default DatePickerRange;
