import React, {useCallback, useEffect, useMemo, useRef, useState} from 'react';
import moment from 'moment';
import {
    ArrowUpIcon,
    ArrowDownIcon,
    ArrowLeftIcon,
    ArrowRightIcon,
} from '@radix-ui/react-icons';
import Input, {HTMLInputTypes} from '../../components/Input';
import Dropdown from '../../fragments/Dropdown';
import {DayOfWeek, CalendarDirection} from '../../types';
import {CalendarMonth} from './CalendarMonth';
import {DateSet} from './DateSet';
import {getMonthOptions, formatYear, parseYear, isDateInRange} from './helpers';

type CalendarProps = {
    onSelectionChange: (selectionStart: Date, selectionEnd?: Date) => void;
    selectionStart?: Date;
    selectionEnd?: Date;
    highlightStart?: Date;
    highlightEnd?: Date;
    initialVisibleDate?: Date;
    minDateAllowed?: Date;
    maxDateAllowed?: Date;
    disabledDates?: DateSet;
    firstDayOfWeek?: DayOfWeek;
    showOutsideDays?: boolean;
    monthFormat?: string;
    calendarOrientation?: 'vertical' | 'horizontal';
    numberOfMonthsShown?: number;
    daySize?: number;
    direction?: CalendarDirection;
};

const Calendar = ({
    initialVisibleDate = new Date(),
    onSelectionChange,
    selectionStart,
    selectionEnd,
    highlightStart,
    highlightEnd,
    minDateAllowed,
    maxDateAllowed,
    disabledDates,
    firstDayOfWeek,
    showOutsideDays,
    monthFormat,
    calendarOrientation,
    numberOfMonthsShown = 1,
    daySize,
    direction = CalendarDirection.LeftToRight,
}: CalendarProps) => {
    const [activeYear, setActiveYear] = useState(() =>
        initialVisibleDate.getFullYear()
    );
    const [activeMonth, setActiveMonth] = useState(() =>
        initialVisibleDate.getMonth()
    );

    // Initialize focused date: use selectionStart if it's in the visible month, otherwise first of month
    const [focusedDate, setFocusedDate] = useState(() => {
        if (
            selectionStart &&
            selectionStart.getMonth() === initialVisibleDate.getMonth() &&
            selectionStart.getFullYear() === initialVisibleDate.getFullYear()
        ) {
            return selectionStart;
        }
        return new Date(
            initialVisibleDate.getFullYear(),
            initialVisibleDate.getMonth(),
            1
        );
    });
    const [highlightedDates, setHighlightedDates] = useState(new DateSet());
    const calendarContainerRef = useRef(document.createElement('div'));
    const scrollAccumulatorRef = useRef(0);
    const prevFocusedDateRef = useRef(focusedDate);

    // Compute display year as a number based on month_format
    const displayYear = useMemo(() => {
        const formatted = formatYear(activeYear, monthFormat);
        return parseInt(formatted, 10);
    }, [activeYear, monthFormat]);

    // First day of the active month (used for navigation and range calculations)
    const activeMonthStart = useMemo(
        () => moment([activeYear, activeMonth, 1]),
        [activeYear, activeMonth]
    );

    useEffect(() => {
        // Syncs activeMonth/activeYear to focusedDate when focusedDate changes
        if (focusedDate.getTime() === prevFocusedDateRef.current.getTime()) {
            return;
        }
        prevFocusedDateRef.current = focusedDate;

        // Calculate visible month range (centered on activeMonth/activeYear)
        const halfRange = Math.floor((numberOfMonthsShown - 1) / 2);
        const activeMonthStart = moment([activeYear, activeMonth, 1]);
        const visibleStart = activeMonthStart
            .clone()
            .subtract(halfRange, 'months')
            .toDate();
        const visibleEnd = activeMonthStart
            .clone()
            .add(halfRange, 'months')
            .toDate();

        // Sync activeMonth/activeYear to focusedDate if focused month is outside visible range
        const focusedMonthStart = new Date(
            focusedDate.getFullYear(),
            focusedDate.getMonth(),
            1
        );
        if (!isDateInRange(focusedMonthStart, visibleStart, visibleEnd)) {
            setActiveMonth(focusedDate.getMonth());
            setActiveYear(focusedDate.getFullYear());
        }
    }, [focusedDate, activeMonth, activeYear, numberOfMonthsShown]);

    useEffect(() => {
        setHighlightedDates(DateSet.fromRange(highlightStart, highlightEnd));
    }, [highlightStart, highlightEnd]);

    const selectedDates = useMemo(
        () => DateSet.fromRange(selectionStart, selectionEnd),
        [selectionStart, selectionEnd]
    );

    const monthOptions = useMemo(
        () =>
            getMonthOptions(
                activeYear,
                monthFormat,
                minDateAllowed,
                maxDateAllowed
            ),
        [activeYear, monthFormat, minDateAllowed, maxDateAllowed]
    );

    const handleWheel = useCallback(
        (e: WheelEvent) => {
            e.preventDefault();

            // Accumulate scroll delta until threshold is reached, then change the active month
            // This respects OS scroll speed settings and works well with trackpads
            const threshold = 100; // Adjust this to control sensitivity

            scrollAccumulatorRef.current += e.deltaY;

            if (Math.abs(scrollAccumulatorRef.current) >= threshold) {
                const currentDate = moment([activeYear, activeMonth, 1]);
                const newDate =
                    scrollAccumulatorRef.current > 0
                        ? currentDate.clone().add(1, 'month')
                        : currentDate.clone().subtract(1, 'month');

                // Check if the new month is within allowed range
                const newMonth = newDate.toDate();
                const isWithinRange =
                    (!minDateAllowed ||
                        newMonth >=
                            moment(minDateAllowed).startOf('month').toDate()) &&
                    (!maxDateAllowed ||
                        newMonth <=
                            moment(maxDateAllowed).startOf('month').toDate());

                if (isWithinRange) {
                    setActiveYear(newDate.year());
                    setActiveMonth(newDate.month());
                }
                scrollAccumulatorRef.current = 0; // Reset accumulator after month change
            }
        },
        [activeYear, activeMonth, minDateAllowed, maxDateAllowed]
    );

    useEffect(() => {
        // Add listener with passive: false to allow preventDefault
        calendarContainerRef.current.addEventListener('wheel', handleWheel, {
            passive: false,
        });

        return () => {
            calendarContainerRef.current?.removeEventListener(
                'wheel',
                handleWheel
            );
        };
    }, [handleWheel]);

    const handlePreviousMonth = useCallback(() => {
        const currentDate = moment([activeYear, activeMonth, 1]);
        // In RTL mode, "previous" button actually goes to next month
        const newDate =
            direction === CalendarDirection.RightToLeft
                ? currentDate.clone().add(1, 'month')
                : currentDate.clone().subtract(1, 'month');
        const newMonth = newDate.toDate();

        const isWithinRange =
            !minDateAllowed ||
            newMonth >= moment(minDateAllowed).startOf('month').toDate();

        if (isWithinRange) {
            setActiveYear(newDate.year());
            setActiveMonth(newDate.month());
        }
    }, [activeYear, activeMonth, minDateAllowed, direction]);

    const handleNextMonth = useCallback(() => {
        const currentDate = moment([activeYear, activeMonth, 1]);
        // In RTL mode, "next" button actually goes to previous month
        const newDate =
            direction === CalendarDirection.RightToLeft
                ? currentDate.clone().subtract(1, 'month')
                : currentDate.clone().add(1, 'month');
        const newMonth = newDate.toDate();

        const isWithinRange =
            !maxDateAllowed ||
            newMonth <= moment(maxDateAllowed).startOf('month').toDate();

        if (isWithinRange) {
            setActiveYear(newDate.year());
            setActiveMonth(newDate.month());
        }
    }, [activeYear, activeMonth, maxDateAllowed, direction]);

    const isPreviousMonthDisabled = useMemo(() => {
        if (!minDateAllowed) {
            return false;
        }
        const currentDate = moment([activeYear, activeMonth, 1]);
        const prevMonth = currentDate.clone().subtract(1, 'month').toDate();
        return prevMonth < moment(minDateAllowed).startOf('month').toDate();
    }, [activeYear, activeMonth, minDateAllowed]);

    const isNextMonthDisabled = useMemo(() => {
        if (!maxDateAllowed) {
            return false;
        }
        const currentDate = moment([activeYear, activeMonth, 1]);
        const nextMonth = currentDate.clone().add(1, 'month').toDate();
        return nextMonth > moment(maxDateAllowed).startOf('month').toDate();
    }, [activeYear, activeMonth, maxDateAllowed]);

    const isVertical = calendarOrientation === 'vertical';
    const PreviousMonthIcon = isVertical ? ArrowUpIcon : ArrowLeftIcon;
    const NextMonthIcon = isVertical ? ArrowDownIcon : ArrowRightIcon;

    return (
        <div
            className="dash-datepicker-calendar-wrapper"
            style={{'--day-size': `${daySize}px`} as React.CSSProperties}
        >
            <div className="dash-datepicker-controls">
                <button
                    className="dash-datepicker-month-nav"
                    onClick={handlePreviousMonth}
                    disabled={isPreviousMonthDisabled}
                    aria-label="Previous month"
                >
                    <PreviousMonthIcon />
                </button>
                <Dropdown
                    options={monthOptions}
                    value={activeMonth}
                    maxHeight={250}
                    searchable={false}
                    setProps={({value}) => {
                        if (Number.isInteger(value)) {
                            setActiveMonth(value as number);
                        }
                    }}
                />
                <Input
                    type={HTMLInputTypes.number}
                    debounce={0.5}
                    value={displayYear}
                    min={
                        minDateAllowed
                            ? moment(minDateAllowed).year()
                            : undefined
                    }
                    max={
                        maxDateAllowed
                            ? moment(maxDateAllowed).year()
                            : undefined
                    }
                    setProps={({value}) => {
                        if (typeof value === 'number') {
                            const parsed = parseYear(String(value));
                            if (parsed !== undefined) {
                                setActiveYear(parsed);
                            }
                        }
                    }}
                />
                <button
                    className="dash-datepicker-month-nav"
                    onClick={handleNextMonth}
                    disabled={isNextMonthDisabled}
                    aria-label="Next month"
                >
                    <NextMonthIcon />
                </button>
            </div>
            <div
                className="dash-datepicker-calendar-container"
                ref={calendarContainerRef}
                dir={direction}
                style={{
                    flexDirection:
                        calendarOrientation === 'vertical' ? 'column' : 'row',
                }}
            >
                {Array.from({length: numberOfMonthsShown}, (_, i) => {
                    // Center the view: start from (numberOfMonthsShown - 1) / 2 months before activeMonth
                    const offset =
                        i - Math.floor((numberOfMonthsShown - 1) / 2);
                    const monthDate = moment([activeYear, activeMonth, 1]).add(
                        offset,
                        'months'
                    );
                    return (
                        <CalendarMonth
                            key={i}
                            year={monthDate.year()}
                            month={monthDate.month()}
                            minDateAllowed={minDateAllowed}
                            maxDateAllowed={maxDateAllowed}
                            disabledDates={disabledDates}
                            dateFocused={focusedDate}
                            onDayFocused={setFocusedDate}
                            datesSelected={selectedDates}
                            onDaySelected={onSelectionChange}
                            datesHighlighted={highlightedDates}
                            onDaysHighlighted={setHighlightedDates}
                            firstDayOfWeek={firstDayOfWeek}
                            showOutsideDays={showOutsideDays}
                            daySize={daySize}
                            monthFormat={monthFormat}
                            showMonthHeader={numberOfMonthsShown > 1}
                            direction={direction}
                        />
                    );
                })}
            </div>
        </div>
    );
};

export default Calendar;
