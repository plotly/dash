import React, {useCallback, useMemo} from 'react';
import moment from 'moment';
import CalendarDay from './CalendarDay';
import CalendarDayPadding from './CalendarDayPadding';
import {createMonthGrid} from './createMonthGrid';
import {isDateInRange, isDateDisabled, isSameDay} from './helpers';
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
    firstDayOfWeek?: number; // 0-7
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
        return Array.from({length: 7}, (_, i) =>
            moment()
                .day((i + firstDayOfWeek) % 7)
                .format('dd')
        );
    }, [firstDayOfWeek]);

    const handleKeyDown = useCallback(
        (e: React.KeyboardEvent, date: Date) => {
            const m = moment(date);
            let newDate: moment.Moment | null = null;

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
                            ? m.subtract(1, 'day')
                            : m.add(1, 'day');
                    break;
                case 'ArrowLeft':
                    newDate =
                        direction === CalendarDirection.RightToLeft
                            ? m.add(1, 'day')
                            : m.subtract(1, 'day');
                    break;
                case 'ArrowDown':
                    newDate = m.add(1, 'week');
                    break;
                case 'ArrowUp':
                    newDate = m.subtract(1, 'week');
                    break;
                case 'PageDown':
                    newDate = m.add(1, 'month');
                    break;
                case 'PageUp':
                    newDate = m.subtract(1, 'month');
                    break;
                case 'Home':
                    // Navigate to week start (respecting firstDayOfWeek)
                    newDate = m.clone().day(firstDayOfWeek);
                    // If we went forward, adjust backward to current week
                    if (newDate.isAfter(m, 'day')) {
                        newDate.subtract(1, 'week');
                    }
                    break;
                case 'End':
                    // Navigate to week end (respecting firstDayOfWeek)
                    newDate = m.clone().day((firstDayOfWeek + 6) % 7);
                    // If we went backward, adjust forward to current week
                    if (newDate.isBefore(m, 'day')) {
                        newDate.add(1, 'week');
                    }
                    break;
                default:
                    return;
            }

            if (newDate) {
                e.preventDefault();
                const newDateObj = newDate.toDate();
                if (isDateInRange(newDateObj, minDateAllowed, maxDateAllowed)) {
                    onDayFocused?.(newDateObj);
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
