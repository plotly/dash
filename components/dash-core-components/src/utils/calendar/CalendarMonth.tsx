import React, {useCallback, useMemo} from 'react';
import {
    addDays,
    subDays,
    addWeeks,
    subWeeks,
    addMonths,
    subMonths,
    setDay,
    startOfWeek,
    endOfWeek,
    format,
} from 'date-fns';
import type {Day} from 'date-fns';
import CalendarDay from './CalendarDay';
import CalendarDayPadding from './CalendarDayPadding';
import {createMonthGrid} from './createMonthGrid';
import {
    isDateInRange,
    isDateDisabled,
    isSameDay,
    getUserLocale,
} from './helpers';
import {CalendarDirection} from '../../types';
import '../../components/css/calendar.css';
import CalendarMonthHeader from './CalendarMonthHeader';

export enum NavigationDirection {
    Backward = -1,
    Forward = 1,
}

type CalendarMonthProps = {
    year: number;
    month: number; // 0-11 representing January-December;
    dateFocused?: Date;
    selectedDates?: Date[];
    highlightedDatesRange?: [Date, Date];
    minDateAllowed?: Date;
    maxDateAllowed?: Date;
    disabledDates?: Date[];
    onSelectionStart?: (date: Date) => void;
    onSelectionEnd?: (date: Date) => void;
    onDayFocused?: (date: Date) => void;
    onDaysHighlighted?: (date: Date) => void;
    firstDayOfWeek?: Day;
    showOutsideDays?: boolean;
    daySize?: number;
    monthFormat?: string;
    showMonthHeader?: boolean;
    direction?: CalendarDirection;
};

export const CalendarMonth = ({
    year,
    month,
    onSelectionStart,
    onSelectionEnd,
    onDayFocused,
    onDaysHighlighted,
    selectedDates = [],
    highlightedDatesRange,
    minDateAllowed,
    maxDateAllowed,
    disabledDates,
    monthFormat,
    firstDayOfWeek = 0,
    showOutsideDays = true,
    // eslint-disable-next-line no-magic-numbers
    daySize = 36,
    showMonthHeader = false,
    direction = CalendarDirection.LeftToRight,
    ...props
}: CalendarMonthProps): JSX.Element => {
    const gridDates = useMemo(
        () => createMonthGrid(year, month, firstDayOfWeek, showOutsideDays),
        [year, month, firstDayOfWeek, showOutsideDays]
    );

    const isDisabled = useCallback(
        (date: Date): boolean => {
            return isDateDisabled(
                date,
                minDateAllowed,
                maxDateAllowed,
                disabledDates
            );
        },
        [minDateAllowed, maxDateAllowed, disabledDates]
    );

    const computeIsOutside = useCallback(
        (date: Date): boolean => {
            return date.getMonth() !== month;
        },
        [month]
    );

    const daysOfTheWeek = useMemo(() => {
        return Array.from({length: 7}, (_, i) => {
            const date = setDay(new Date(), (i + firstDayOfWeek) % 7);
            return format(date, 'EEEEEE', {locale: getUserLocale()});
        });
    }, [firstDayOfWeek]);

    const handleKeyDown = useCallback(
        (e: React.KeyboardEvent, date: Date) => {
            let newDate: Date | null = null;

            switch (e.key) {
                case ' ':
                case 'Enter': {
                    e.preventDefault();
                    const isOutside = computeIsOutside(date);
                    if (!isDisabled(date) && (!isOutside || showOutsideDays)) {
                        // Keyboard selection: only call onSelectionEnd
                        // Calendar will handle completing immediately by setting both start and end
                        onSelectionEnd?.(date);
                    }
                    return;
                }
                case 'ArrowRight':
                    newDate =
                        direction === CalendarDirection.RightToLeft
                            ? subDays(date, 1)
                            : addDays(date, 1);
                    break;
                case 'ArrowLeft':
                    newDate =
                        direction === CalendarDirection.RightToLeft
                            ? addDays(date, 1)
                            : subDays(date, 1);
                    break;
                case 'ArrowDown':
                    newDate = addWeeks(date, 1);
                    break;
                case 'ArrowUp':
                    newDate = subWeeks(date, 1);
                    break;
                case 'PageDown':
                    newDate = addMonths(date, 1);
                    break;
                case 'PageUp':
                    newDate = subMonths(date, 1);
                    break;
                case 'Home':
                    newDate = startOfWeek(date, {weekStartsOn: firstDayOfWeek});
                    break;
                case 'End':
                    newDate = endOfWeek(date, {weekStartsOn: firstDayOfWeek});
                    break;
                default:
                    return;
            }

            if (newDate) {
                e.preventDefault();
                if (isDateInRange(newDate, minDateAllowed, maxDateAllowed)) {
                    onDayFocused?.(newDate);
                }
            }
        },
        [
            onDayFocused,
            onSelectionStart,
            onSelectionEnd,
            computeIsOutside,
            isDisabled,
            showOutsideDays,
            minDateAllowed,
            maxDateAllowed,
            direction,
            firstDayOfWeek,
        ]
    );

    const calendarWidth = daySize * 7 + 16; // 16px for table padding

    return (
        <table
            className="dash-datepicker-calendar"
            style={{width: `${calendarWidth}px`}}
        >
            <thead>
                {showMonthHeader && (
                    <tr>
                        <CalendarMonthHeader
                            year={year}
                            month={month}
                            monthFormat={monthFormat}
                        />
                    </tr>
                )}
                <tr>
                    {daysOfTheWeek.map((day, i) => (
                        <th key={i}>
                            <span>{day}</span>
                        </th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {gridDates.map((week, i) => (
                    <tr key={i} className="dash-datepicker-calendar-week">
                        {week.map((date, j) =>
                            date ? (
                                <CalendarDay
                                    key={j}
                                    date={date}
                                    isOutside={computeIsOutside(date)}
                                    showOutsideDays={showOutsideDays}
                                    onMouseDown={() => {
                                        onDaysHighlighted?.(date);
                                        onSelectionStart?.(date);
                                    }}
                                    onMouseUp={() => onSelectionEnd?.(date)}
                                    onMouseEnter={() =>
                                        onDaysHighlighted?.(date)
                                    }
                                    onKeyDown={e => handleKeyDown(e, date)}
                                    isFocused={isSameDay(
                                        date,
                                        props.dateFocused
                                    )}
                                    isSelected={selectedDates.some(d =>
                                        isSameDay(date, d)
                                    )}
                                    isHighlighted={
                                        highlightedDatesRange !== undefined &&
                                        isDateInRange(
                                            date,
                                            highlightedDatesRange[0],
                                            highlightedDatesRange[1]
                                        )
                                    }
                                    isDisabled={isDisabled(date)}
                                />
                            ) : (
                                <CalendarDayPadding key={j} />
                            )
                        )}
                    </tr>
                ))}
            </tbody>
        </table>
    );
};
