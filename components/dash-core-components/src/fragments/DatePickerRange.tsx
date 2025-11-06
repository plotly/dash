import React, {useCallback, useEffect, useMemo, useRef, useState} from 'react';
import * as Popover from '@radix-ui/react-popover';
import {
    CalendarIcon,
    CaretDownIcon,
    Cross1Icon,
    ArrowLeftIcon,
    ArrowRightIcon,
} from '@radix-ui/react-icons';
import AutosizeInput from 'react-input-autosize';
import Calendar, {CalendarHandle} from '../utils/calendar/Calendar';
import {DatePickerRangeProps, CalendarDirection} from '../types';
import {
    dateAsStr,
    strAsDate,
    formatDate,
    isDateDisabled,
    isSameDay,
} from '../utils/calendar/helpers';
import '../components/css/datepickers.css';
import uuid from 'uniqid';
import moment from 'moment';

const DatePickerRange = ({
    id,
    className,
    start_date,
    end_date,
    min_date_allowed,
    max_date_allowed,
    initial_visible_month = start_date ?? min_date_allowed ?? max_date_allowed,
    disabled_days,
    minimum_nights,
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
    const initialCalendarDate =
        strAsDate(initial_visible_month) ||
        internalStartDate ||
        internalEndDate;

    const minDate = strAsDate(min_date_allowed);
    const maxDate = strAsDate(max_date_allowed);
    const disabledDates = useMemo(() => {
        const baseDates =
            disabled_days
                ?.map(d => strAsDate(d))
                .filter((d): d is Date => d !== undefined) || [];

        // Add minimum_nights constraint: disable dates within the minimum nights range
        if (
            internalStartDate &&
            minimum_nights &&
            minimum_nights > 0 &&
            !internalEndDate
        ) {
            const minimumNightsDates: Date[] = [];
            for (let i = 1; i < minimum_nights; i++) {
                minimumNightsDates.push(
                    moment(internalStartDate).add(i, 'day').toDate()
                );
                minimumNightsDates.push(
                    moment(internalStartDate).subtract(i, 'day').toDate()
                );
            }
            return [...baseDates, ...minimumNightsDates];
        }

        return baseDates;
    }, [disabled_days, internalStartDate, internalEndDate, minimum_nights]);

    const [isCalendarOpen, setIsCalendarOpen] = useState(false);
    const [startInputValue, setStartInputValue] = useState(
        formatDate(internalStartDate, display_format)
    );
    const [endInputValue, setEndInputValue] = useState(
        formatDate(internalEndDate, display_format)
    );

    const containerRef = useRef<HTMLDivElement>(null);
    const startInputRef = useRef<HTMLInputElement | null>(null);
    const endInputRef = useRef<HTMLInputElement | null>(null);
    const calendarRef = useRef<CalendarHandle>(null);

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
    }, [isCalendarOpen, startInputValue]);

    const sendStartInputAsDate = useCallback(
        (focusCalendar = false) => {
            if (startInputValue) {
                setInternalStartDate(undefined);
            }
            const parsed = strAsDate(startInputValue, display_format);
            const isValid =
                parsed &&
                !isDateDisabled(parsed, minDate, maxDate, disabledDates);

            if (isValid) {
                setInternalStartDate(parsed);
                if (focusCalendar) {
                    calendarRef.current?.focusDate(parsed);
                } else {
                    calendarRef.current?.setVisibleDate(parsed);
                }
            } else {
                // Invalid or disabled input: revert to previous valid date with proper formatting
                const previousDate = strAsDate(start_date);
                setStartInputValue(
                    previousDate ? formatDate(previousDate, display_format) : ''
                );
                if (focusCalendar) {
                    calendarRef.current?.focusDate(previousDate);
                }
            }
        },
        [
            startInputValue,
            display_format,
            start_date,
            minDate,
            maxDate,
            disabledDates,
        ]
    );

    const sendEndInputAsDate = useCallback(
        (focusCalendar = false) => {
            if (endInputValue === '') {
                setInternalEndDate(undefined);
            }
            const parsed = strAsDate(endInputValue, display_format);
            const isValid =
                parsed &&
                !isDateDisabled(parsed, minDate, maxDate, disabledDates);

            if (isValid) {
                setInternalEndDate(parsed);
                if (focusCalendar) {
                    calendarRef.current?.focusDate(parsed);
                } else {
                    calendarRef.current?.setVisibleDate(parsed);
                }
            } else {
                // Invalid or disabled input: revert to previous valid date with proper formatting
                const previousDate = strAsDate(end_date);
                setEndInputValue(
                    previousDate ? formatDate(previousDate, display_format) : ''
                );
                if (focusCalendar) {
                    calendarRef.current?.focusDate(previousDate);
                }
            }
        },
        [
            endInputValue,
            display_format,
            end_date,
            minDate,
            maxDate,
            disabledDates,
        ]
    );

    const clearSelection = useCallback(
        e => {
            setInternalStartDate(undefined);
            setInternalEndDate(undefined);
            startInputRef.current?.focus();
            e.preventDefault();
            e.stopPropagation();
            if (reopen_calendar_on_clear) {
                setIsCalendarOpen(true);
            }
        },
        [reopen_calendar_on_clear]
    );

    const handleStartInputKeyDown = useCallback(
        (e: React.KeyboardEvent<HTMLInputElement>) => {
            if (['ArrowUp', 'ArrowDown'].includes(e.key)) {
                e.preventDefault();
                sendStartInputAsDate(true);
                if (!isCalendarOpen) {
                    // open the calendar after resolving prop changes, so that
                    // it opens with the correct date showing
                    setTimeout(() => setIsCalendarOpen(true), 0);
                }
            } else if (['Enter', 'Tab'].includes(e.key)) {
                sendStartInputAsDate();
            }
        },
        [isCalendarOpen, sendStartInputAsDate]
    );

    const handleEndInputKeyDown = useCallback(
        (e: React.KeyboardEvent<HTMLInputElement>) => {
            if (['ArrowUp', 'ArrowDown'].includes(e.key)) {
                e.preventDefault();
                sendEndInputAsDate(true);
                if (!isCalendarOpen) {
                    // open the calendar after resolving prop changes, so that
                    // it opens with the correct date showing
                    setTimeout(() => setIsCalendarOpen(true), 0);
                }
            } else if (['Enter', 'Tab'].includes(e.key)) {
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

    const ArrowIcon =
        direction === CalendarDirection.LeftToRight
            ? ArrowRightIcon
            : ArrowLeftIcon;

    const handleSelectionChange = useCallback(
        (start?: Date, end?: Date) => {
            const isNewSelection =
                isSameDay(start, end) &&
                ((!internalStartDate && !internalEndDate) ||
                    (internalStartDate && internalEndDate));

            if (isNewSelection) {
                setInternalStartDate(start);
                setInternalEndDate(undefined);
            } else {
                // Normalize dates: ensure start <= end
                if (start && end && start > end) {
                    setInternalStartDate(end);
                    setInternalEndDate(start);
                } else {
                    setInternalStartDate(start);
                    setInternalEndDate(end);
                }

                if (end && !stay_open_on_select) {
                    setIsCalendarOpen(false);
                }
            }
        },
        [internalStartDate, internalEndDate, stay_open_on_select]
    );

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
                        onClick={e => {
                            e.preventDefault();
                            if (!isCalendarOpen && !disabled) {
                                setIsCalendarOpen(true);
                            }
                        }}
                    >
                        <CalendarIcon className="dash-datepicker-trigger-icon" />
                        <AutosizeInput
                            inputRef={node => {
                                startInputRef.current = node;
                            }}
                            type="text"
                            id={start_date_id || accessibleId}
                            inputClassName="dash-datepicker-input dash-datepicker-start-date"
                            value={startInputValue}
                            onChange={e => setStartInputValue(e.target.value)}
                            onKeyDown={handleStartInputKeyDown}
                            onFocus={() => {
                                if (internalStartDate) {
                                    calendarRef.current?.setVisibleDate(
                                        internalStartDate
                                    );
                                }
                            }}
                            placeholder={start_date_placeholder_text}
                            disabled={disabled}
                            dir={direction}
                            aria-label={start_date_placeholder_text}
                        />
                        <ArrowIcon />
                        <AutosizeInput
                            inputRef={node => {
                                endInputRef.current = node;
                            }}
                            type="text"
                            id={end_date_id || accessibleId + '-end-date'}
                            inputClassName="dash-datepicker-input dash-datepicker-end-date"
                            value={endInputValue}
                            onChange={e => setEndInputValue(e.target.value)}
                            onKeyDown={handleEndInputKeyDown}
                            onFocus={() => {
                                if (internalEndDate) {
                                    calendarRef.current?.setVisibleDate(
                                        internalEndDate
                                    );
                                }
                            }}
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
                        <Calendar
                            ref={calendarRef}
                            initialVisibleDate={initialCalendarDate}
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
                            onSelectionChange={handleSelectionChange}
                        />
                    </Popover.Content>
                </Popover.Portal>
            </Popover.Root>
        </div>
    );
};

export default DatePickerRange;
