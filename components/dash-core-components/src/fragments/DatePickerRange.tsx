import React, {useCallback, useEffect, useMemo, useRef, useState} from 'react';
import * as Popover from '@radix-ui/react-popover';
import {
    CalendarIcon,
    CaretDownIcon,
    Cross1Icon,
    ArrowRightIcon,
} from '@radix-ui/react-icons';
import Calendar from '../utils/calendar/Calendar';
import {DatePickerRangeProps, CalendarDirection} from '../types';
import {
    dateAsStr,
    strAsDate,
    formatDate,
    isDateDisabled,
    isSameDay,
} from '../utils/calendar/helpers';
import {DateSet} from '../utils/calendar/DateSet';
import '../components/css/datepickers.css';
import uuid from 'uniqid';

const DatePickerRange = ({
    id,
    className,
    start_date,
    end_date,
    min_date_allowed,
    max_date_allowed,
    initial_visible_month = start_date ?? min_date_allowed ?? max_date_allowed,
    disabled_days,
    first_day_of_week,
    show_outside_days,
    clearable,
    reopen_calendar_on_clear,
    disabled,
    display_format,
    month_format = 'MMMM YYYY',
    stay_open_on_select,
    is_RTL = false,
    setProps,
    style,
    // eslint-disable-next-line no-magic-numbers
    day_size = 34,
    number_of_months_shown = 1,
    calendar_orientation,
    updatemode,
    start_date_id,
    end_date_id,
    start_date_placeholder_text = 'Start Date',
    end_date_placeholder_text = 'End Date',
}: DatePickerRangeProps) => {
    const [internalStartDate, setInternalStartDate] = useState(
        strAsDate(start_date)
    );
    const [internalEndDate, setInternalEndDate] = useState(strAsDate(end_date));
    const direction = is_RTL
        ? CalendarDirection.RightToLeft
        : CalendarDirection.LeftToRight;
    const initialMonth = strAsDate(initial_visible_month);
    const minDate = strAsDate(min_date_allowed);
    const maxDate = strAsDate(max_date_allowed);
    const disabledDates = useMemo(
        () => new DateSet(disabled_days),
        [disabled_days]
    );

    const [isCalendarOpen, setIsCalendarOpen] = useState(false);
    const [startInputValue, setStartInputValue] = useState<string>(
        (internalStartDate && formatDate(internalStartDate, display_format)) ??
            ''
    );
    const [endInputValue, setEndInputValue] = useState<string>(
        (internalEndDate && formatDate(internalEndDate, display_format)) ?? ''
    );

    const containerRef = useRef<HTMLDivElement>(null);
    const startInputRef = useRef<HTMLInputElement>(null);
    const endInputRef = useRef<HTMLInputElement>(null);
    const calendarRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        setInternalStartDate(strAsDate(start_date));
    }, [start_date]);

    useEffect(() => {
        setInternalEndDate(strAsDate(end_date));
    }, [end_date]);

    useEffect(() => {
        setStartInputValue(formatDate(internalStartDate, display_format));
    }, [internalStartDate, display_format]);

    useEffect(() => {
        setEndInputValue(formatDate(internalEndDate, display_format));
    }, [internalEndDate, display_format]);

    useEffect(() => {
        // Controls whether or not to call `setProps`
        const startChanged = !isSameDay(start_date, internalStartDate);
        const endChanged = !isSameDay(end_date, internalEndDate);

        const newDates: Partial<DatePickerRangeProps> = {
            ...(startChanged && {start_date: dateAsStr(internalStartDate)}),
            ...(endChanged && {end_date: dateAsStr(internalEndDate)}),
        };

        const numPropsRequiredForUpdate = updatemode === 'bothdates' ? 2 : 1;
        if (Object.keys(newDates).length >= numPropsRequiredForUpdate) {
            setProps(newDates);
        }
    }, [start_date, internalStartDate, end_date, internalEndDate, updatemode]);

    useEffect(() => {
        // Keeps focus on the component when the calendar closes
        if (!isCalendarOpen) {
            if (!startInputValue) {
                startInputRef.current?.focus();
            } else {
                endInputRef.current?.focus();
            }
        }
    }, [isCalendarOpen]);

    const sendStartInputAsDate = useCallback(() => {
        const parsed = strAsDate(startInputValue, display_format);
        const isValid =
            parsed && !isDateDisabled(parsed, minDate, maxDate, disabledDates);

        if (isValid) {
            setInternalStartDate(parsed);
        } else {
            // Invalid or disabled input: revert to previous valid date with proper formatting
            const previousDate = strAsDate(start_date);
            setStartInputValue(
                previousDate ? formatDate(previousDate, display_format) : ''
            );
        }
    }, [
        startInputValue,
        display_format,
        start_date,
        minDate,
        maxDate,
        disabledDates,
    ]);

    const sendEndInputAsDate = useCallback(() => {
        const parsed = strAsDate(endInputValue, display_format);
        const isValid =
            parsed && !isDateDisabled(parsed, minDate, maxDate, disabledDates);

        if (isValid) {
            setInternalEndDate(parsed);
        } else {
            // Invalid or disabled input: revert to previous valid date with proper formatting
            const previousDate = strAsDate(end_date);
            setEndInputValue(
                previousDate ? formatDate(previousDate, display_format) : ''
            );
        }
    }, [
        endInputValue,
        display_format,
        end_date,
        minDate,
        maxDate,
        disabledDates,
    ]);

    const clearSelection = useCallback(
        e => {
            e.preventDefault();
            setInternalStartDate(undefined);
            setInternalEndDate(undefined);
            if (reopen_calendar_on_clear) {
                setIsCalendarOpen(true);
            } else {
                startInputRef.current?.focus();
            }
        },
        [reopen_calendar_on_clear]
    );

    const handleStartInputKeyDown = useCallback(
        (e: React.KeyboardEvent<HTMLInputElement>) => {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (!isCalendarOpen) {
                    sendStartInputAsDate();
                    // open the calendar after resolving prop changes, so that
                    // it opens with the correct date showing
                    setTimeout(() => setIsCalendarOpen(true), 0);
                }
            } else if (e.key === 'Enter') {
                sendStartInputAsDate();
            }
        },
        [isCalendarOpen, sendStartInputAsDate]
    );

    const handleEndInputKeyDown = useCallback(
        (e: React.KeyboardEvent<HTMLInputElement>) => {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (!isCalendarOpen) {
                    sendEndInputAsDate();
                    // open the calendar after resolving prop changes, so that
                    // it opens with the correct date showing
                    setTimeout(() => setIsCalendarOpen(true), 0);
                }
            } else if (e.key === 'Enter') {
                sendEndInputAsDate();
            }
        },
        [isCalendarOpen, sendEndInputAsDate]
    );

    const accessibleId = id ?? uuid();
    let classNames = 'dash-datepicker-input-wrapper';
    if (disabled) {
        classNames += ' dash-datepicker-input-wrapper-disabled';
    }
    if (className) {
        classNames += ' ' + className;
    }

    return (
        <div className="dash-datepicker" ref={containerRef}>
            <Popover.Root
                open={!disabled && isCalendarOpen}
                onOpenChange={disabled ? undefined : setIsCalendarOpen}
            >
                <Popover.Trigger asChild disabled={disabled}>
                    <div
                        id={accessibleId + '-wrapper'}
                        className={classNames}
                        style={style}
                        aria-labelledby={`${accessibleId} ${accessibleId}-end-date ${start_date_id} ${end_date_id}`}
                        aria-haspopup="dialog"
                        aria-expanded={isCalendarOpen}
                        aria-disabled={disabled}
                    >
                        <CalendarIcon className="dash-datepicker-trigger-icon" />
                        <input
                            ref={startInputRef}
                            type="text"
                            id={start_date_id || accessibleId}
                            className="dash-datepicker-input dash-datepicker-start-date"
                            value={startInputValue}
                            onChange={e => setStartInputValue(e.target.value)}
                            onKeyDown={handleStartInputKeyDown}
                            onBlur={sendStartInputAsDate}
                            placeholder={start_date_placeholder_text}
                            disabled={disabled}
                            dir={direction}
                            aria-label={start_date_placeholder_text}
                        />
                        <ArrowRightIcon />
                        <input
                            ref={endInputRef}
                            type="text"
                            id={end_date_id || accessibleId + '-end-date'}
                            className="dash-datepicker-input dash-datepicker-end-date"
                            value={endInputValue}
                            onChange={e => setEndInputValue(e.target.value)}
                            onKeyDown={handleEndInputKeyDown}
                            onBlur={sendEndInputAsDate}
                            placeholder={end_date_placeholder_text}
                            disabled={disabled}
                            dir={direction}
                            aria-label={end_date_placeholder_text}
                        />
                        {clearable && !disabled && (
                            <a
                                className="dash-datepicker-clear"
                                onClick={clearSelection}
                                aria-label="Clear Dates"
                            >
                                <Cross1Icon />
                            </a>
                        )}
                        <CaretDownIcon className="dash-datepicker-caret-icon" />
                    </div>
                </Popover.Trigger>

                <Popover.Portal container={containerRef.current}>
                    <Popover.Content
                        className="dash-datepicker-content"
                        align="start"
                        sideOffset={5}
                        onOpenAutoFocus={e => e.preventDefault()}
                    >
                        <div ref={calendarRef}>
                            <Calendar
                                initialVisibleDate={
                                    initialMonth ||
                                    internalStartDate ||
                                    internalEndDate
                                }
                                selectionStart={internalStartDate}
                                selectionEnd={internalEndDate}
                                minDateAllowed={minDate}
                                maxDateAllowed={maxDate}
                                disabledDates={disabledDates}
                                firstDayOfWeek={first_day_of_week}
                                showOutsideDays={show_outside_days}
                                monthFormat={month_format}
                                numberOfMonthsShown={number_of_months_shown}
                                calendarOrientation={calendar_orientation}
                                daySize={day_size}
                                direction={direction}
                                onSelectionChange={(start, end) => {
                                    const isNewSelection =
                                        isSameDay(start, end) &&
                                        ((!internalStartDate &&
                                            !internalEndDate) ||
                                            (internalStartDate &&
                                                internalEndDate));

                                    if (isNewSelection) {
                                        setInternalStartDate(start);
                                        setInternalEndDate(undefined);
                                    } else {
                                        setInternalStartDate(start);
                                        setInternalEndDate(end);

                                        if (end && !stay_open_on_select) {
                                            setIsCalendarOpen(false);
                                        }
                                    }
                                }}
                            />
                        </div>
                    </Popover.Content>
                </Popover.Portal>
            </Popover.Root>
        </div>
    );
};

export default DatePickerRange;
