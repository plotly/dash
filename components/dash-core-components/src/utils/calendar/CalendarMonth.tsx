import React, {useCallback, useMemo, useState} from 'react';
import moment from 'moment';
import CalendarDay from './CalendarDay';
import {createMonthGrid} from './createMonthGrid';
import {formatDate, isDateInRange, isDateDisabled} from './helpers';
import {DateSet} from './DateSet';
import {CalendarDirection} from '../../types';
import '../../components/css/calendar.css';

export enum NavigationDirection {
    Backward = -1,
    Forward = 1,
}

const EmptyRow = () => (
    <tr className="dash-datepicker-calendar-week dash-datepicker-calendar-ghost-row">
        {Array.from({length: 7}, (_, i) => (
            <td key={i} className="dash-datepicker-calendar-ghost-cell">
                <span></span>
            </td>
        ))}
    </tr>
);

type CalendarMonthProps = {
    year: number;
    month: number; // 0-11 representing January-December;
    dateFocused?: Date;
    datesSelected?: DateSet;
    datesHighlighted?: DateSet;
    minDateAllowed?: Date;
    maxDateAllowed?: Date;
    disabledDates?: DateSet;
    onSelectionStart?: (date: Date) => void;
    onSelectionEnd?: (date: Date) => void;
    onDayFocused?: (date: Date) => void;
    onDaysHighlighted?: (days: DateSet) => void;
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
    datesSelected,
    datesHighlighted,
    minDateAllowed,
    maxDateAllowed,
    disabledDates,
    firstDayOfWeek = 0,
    showOutsideDays = false,
    // eslint-disable-next-line no-magic-numbers
    daySize = 36,
    monthFormat,
    showMonthHeader = false,
    direction = CalendarDirection.LeftToRight,
    ...props
}: CalendarMonthProps): JSX.Element => {
    const gridDates = useMemo(
        () => createMonthGrid(year, month, firstDayOfWeek),
        [year, month, firstDayOfWeek]
    );

    const computeIsDisabled = useCallback(
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

    const computeLabel = useCallback(
        (date: Date): string => {
            const isOutside = computeIsOutside(date);
            if (!showOutsideDays && isOutside) {
                return '';
            }
            return String(date.getDate());
        },
        [showOutsideDays, computeIsOutside]
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
                    const isDisabled = computeIsDisabled(date);
                    if (!isDisabled && (!isOutside || showOutsideDays)) {
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
            computeIsDisabled,
            showOutsideDays,
            minDateAllowed,
            maxDateAllowed,
            direction,
            firstDayOfWeek,
        ]
    );

    const calendarWidth = daySize * 7 + 16; // 16px for table padding

    const monthYearLabel = useMemo(() => {
        return formatDate(new Date(year, month, 1), monthFormat);
    }, [year, month, monthFormat]);

    return (
        <table
            className="dash-datepicker-calendar"
            style={{width: `${calendarWidth}px`}}
        >
            <thead>
                {showMonthHeader && (
                    <tr>
                        <th
                            colSpan={7}
                            className="dash-datepicker-calendar-month-header"
                        >
                            {monthYearLabel}
                        </th>
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
                        {week.map((date, j) => (
                            <CalendarDay
                                key={j}
                                label={computeLabel(date)}
                                isOutside={computeIsOutside(date)}
                                onMouseDown={() => {
                                    onDaysHighlighted?.(new DateSet([date]));
                                    onSelectionStart?.(date);
                                }}
                                onMouseUp={() => {
                                    onSelectionEnd?.(date);
                                }}
                                onMouseEnter={() => {
                                    onDaysHighlighted?.(new DateSet([date]));
                                }}
                                onKeyDown={e => handleKeyDown(e, date)}
                                isFocused={
                                    props.dateFocused !== undefined &&
                                    moment(date).isSame(
                                        props.dateFocused,
                                        'day'
                                    )
                                }
                                isSelected={datesSelected?.has(date) ?? false}
                                isHighlighted={
                                    datesHighlighted?.has(date) ?? false
                                }
                                isDisabled={computeIsDisabled(date)}
                            />
                        ))}
                    </tr>
                ))}
                {Array.from({length: 6 - gridDates.length}, (_, i) => (
                    <EmptyRow key={`empty-${i}`} />
                ))}
            </tbody>
        </table>
    );
};
