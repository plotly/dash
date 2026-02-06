import React, {useCallback, useEffect, useMemo, useRef, useState} from 'react';
import * as Popover from '@radix-ui/react-popover';
import {
    ArrowLeftIcon,
    ArrowRightIcon,
    CaretDownIcon,
    Cross1Icon,
} from '@radix-ui/react-icons';
import {addDays, subDays} from 'date-fns';
import AutosizeInput from 'react-input-autosize';
import uuid from 'uniqid';

import {CalendarDirection, DatePickerRangeProps} from '../types';
import Calendar, {CalendarHandle} from '../utils/calendar/Calendar';
import {
    dateAsStr,
    formatDate,
    isDateDisabled,
    isSameDay,
    strAsDate,
} from '../utils/calendar/helpers';
import {captureCSSForPortal} from '../utils/calendar/cssVariables';
import '../components/css/datepickers.css';

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
    with_portal = false,
    with_full_screen_portal = false,
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
                minimumNightsDates.push(addDays(internalStartDate, i));
                minimumNightsDates.push(subDays(internalStartDate, i));
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
    const hasPortal = with_portal || with_full_screen_portal;

    // Capture CSS variables for portal mode
    const portalStyle = useMemo(() => {
        return hasPortal ? captureCSSForPortal(containerRef) : undefined;
    }, [hasPortal, isCalendarOpen]);

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
        // Controls when setProps is called. Basically, whenever internal state
        // diverges from props (i.e., user interaction)
        const startChanged = !isSameDay(start_date, internalStartDate);
        const endChanged = !isSameDay(end_date, internalEndDate);

        if (!startChanged && !endChanged) {
            return;
        }

        if (internalStartDate && internalEndDate) {
            // Both dates are set - send both
            setProps({
                start_date: dateAsStr(internalStartDate),
                end_date: dateAsStr(internalEndDate),
            });
        } else if (!internalStartDate && !internalEndDate) {
            // Both dates cleared - send undefined for both
            setProps({
                start_date: dateAsStr(internalStartDate),
                end_date: dateAsStr(internalEndDate),
            });
        } else if (updatemode === 'singledate' && internalStartDate) {
            // Only start changed - send just that one
            setProps({start_date: dateAsStr(internalStartDate)});
        } else if (updatemode === 'singledate' && internalEndDate) {
            // Only end changed - send just that one
            setProps({end_date: dateAsStr(internalEndDate)});
        }
    }, [internalStartDate, internalEndDate, updatemode]);

    const isDateAllowed = useCallback(
        (date?: Date): date is Date => {
            return (
                !!date && !isDateDisabled(date, minDate, maxDate, disabledDates)
            );
        },
        [minDate, maxDate, disabledDates]
    );

    const sendStartInputAsDate = useCallback(
        (focusCalendar = false) => {
            if (startInputValue) {
                setInternalStartDate(undefined);
            }
            const parsed = strAsDate(startInputValue, display_format);

            if (isDateAllowed(parsed)) {
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
        [startInputValue, display_format, start_date, isDateAllowed]
    );

    const sendEndInputAsDate = useCallback(
        (focusCalendar = false) => {
            if (endInputValue === '') {
                setInternalEndDate(undefined);
            }
            const parsed = strAsDate(endInputValue, display_format);

            if (isDateAllowed(parsed)) {
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
        [endInputValue, display_format, end_date, isDateAllowed]
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
            if (['ArrowUp', 'ArrowDown', 'Enter'].includes(e.key)) {
                e.preventDefault();
                if (!isCalendarOpen) {
                    setIsCalendarOpen(true);
                }
                // Wait for calendar to mount before focusing
                requestAnimationFrame(() => sendStartInputAsDate(true));
            } else if (e.key === 'Tab') {
                sendStartInputAsDate();
            }
        },
        [isCalendarOpen, sendStartInputAsDate]
    );

    const handleEndInputKeyDown = useCallback(
        (e: React.KeyboardEvent<HTMLInputElement>) => {
            if (['ArrowUp', 'ArrowDown', 'Enter'].includes(e.key)) {
                e.preventDefault();
                if (!isCalendarOpen) {
                    setIsCalendarOpen(true);
                }
                // Wait for calendar to mount before focusing
                requestAnimationFrame(() => sendEndInputAsDate(true));
            } else if (e.key === 'Tab') {
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
                        <AutosizeInput
                            inputRef={node => {
                                startInputRef.current = node;
                            }}
                            type="text"
                            id={start_date_id || accessibleId}
                            inputClassName="dash-datepicker-input dash-datepicker-start-date"
                            value={startInputValue}
                            onChange={e => setStartInputValue(e.target?.value)}
                            onKeyDown={handleStartInputKeyDown}
                            onFocus={() => {
                                if (isCalendarOpen) {
                                    sendStartInputAsDate();
                                }
                            }}
                            placeholder={start_date_placeholder_text}
                            disabled={disabled}
                            dir={direction}
                            aria-label={start_date_placeholder_text}
                        />
                        <ArrowIcon className="dash-datepicker-range-arrow" />
                        <AutosizeInput
                            inputRef={node => {
                                endInputRef.current = node;
                            }}
                            type="text"
                            id={end_date_id || accessibleId + '-end-date'}
                            inputClassName="dash-datepicker-input dash-datepicker-end-date"
                            value={endInputValue}
                            onChange={e => setEndInputValue(e.target?.value)}
                            onKeyDown={handleEndInputKeyDown}
                            onFocus={() => {
                                if (isCalendarOpen) {
                                    sendEndInputAsDate();
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

                <Popover.Portal
                    container={hasPortal ? undefined : containerRef.current}
                >
                    <Popover.Content
                        className={`dash-datepicker-content${
                            hasPortal ? ' dash-datepicker-portal' : ''
                        }${
                            with_full_screen_portal
                                ? ' dash-datepicker-fullscreen'
                                : ''
                        }`}
                        style={portalStyle}
                        align={hasPortal ? 'center' : 'start'}
                        sideOffset={hasPortal ? 0 : 5}
                        avoidCollisions={!hasPortal}
                        onInteractOutside={
                            with_full_screen_portal
                                ? e => e.preventDefault()
                                : undefined
                        }
                        onOpenAutoFocus={e => e.preventDefault()}
                        onCloseAutoFocus={e => {
                            e.preventDefault();
                            // Only focus if focus is not already on one of the inputs
                            const inputs: (Element | null)[] = [
                                startInputRef.current,
                                endInputRef.current,
                            ];
                            if (inputs.includes(document.activeElement)) {
                                return;
                            }

                            // Keeps focus on the component when the calendar closes
                            if (!startInputValue) {
                                startInputRef.current?.focus();
                            } else {
                                endInputRef.current?.focus();
                            }
                        }}
                    >
                        {with_full_screen_portal && (
                            <button
                                className="dash-datepicker-close-button"
                                onClick={() => setIsCalendarOpen(false)}
                                aria-label="Close calendar"
                            >
                                <Cross1Icon />
                            </button>
                        )}
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
