import React, {useCallback, useEffect, useMemo, useRef, useState} from 'react';
import * as Popover from '@radix-ui/react-popover';
import {CaretDownIcon, Cross1Icon} from '@radix-ui/react-icons';
import AutosizeInput from 'react-input-autosize';
import uuid from 'uniqid';

import {CalendarDirection, DatePickerSingleProps} from '../types';
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

const DatePickerSingle = ({
    id,
    className,
    date,
    min_date_allowed,
    max_date_allowed,
    initial_visible_month = date ?? min_date_allowed,
    disabled_days,
    first_day_of_week,
    show_outside_days,
    placeholder = 'Select Date',
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
    with_portal = false,
    with_full_screen_portal = false,
}: DatePickerSingleProps) => {
    const [internalDate, setInternalDate] = useState(strAsDate(date));
    const direction = is_RTL
        ? CalendarDirection.RightToLeft
        : CalendarDirection.LeftToRight;
    const initialMonth = strAsDate(initial_visible_month) || internalDate;
    const minDate = strAsDate(min_date_allowed);
    const maxDate = strAsDate(max_date_allowed);
    const disabledDates = useMemo(() => {
        return disabled_days
            ?.map(d => strAsDate(d))
            .filter((d): d is Date => d !== undefined);
    }, [disabled_days]);

    const [isCalendarOpen, setIsCalendarOpen] = useState(false);
    const [inputValue, setInputValue] = useState<string>(
        (internalDate && formatDate(internalDate, display_format)) ?? ''
    );

    const containerRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement | null>(null);
    const calendarRef = useRef<CalendarHandle>(null);
    const hasPortal = with_portal || with_full_screen_portal;

    // Capture CSS variables for portal mode
    const portalStyle = useMemo(() => {
        return hasPortal ? captureCSSForPortal(containerRef) : undefined;
    }, [hasPortal, isCalendarOpen]);

    useEffect(() => {
        setInternalDate(strAsDate(date));
    }, [date]);

    useEffect(() => {
        setInputValue(formatDate(internalDate, display_format));
    }, [internalDate, display_format]);

    useEffect(() => {
        const dateChanged = !(date && isSameDay(date, internalDate));

        if (dateChanged) {
            setProps({date: dateAsStr(internalDate)});
        }
    }, [internalDate]);

    const parseUserInput = useCallback(
        (focusCalendar = false) => {
            if (inputValue === '') {
                setInternalDate(undefined);
            }
            const parsed = strAsDate(inputValue, display_format);
            const isValid =
                parsed &&
                !isDateDisabled(parsed, minDate, maxDate, disabledDates);

            if (isValid) {
                setInternalDate(parsed);
                if (focusCalendar) {
                    calendarRef.current?.focusDate(parsed);
                } else {
                    calendarRef.current?.setVisibleDate(parsed);
                }
            } else {
                // Invalid or disabled input: revert to previous valid date with proper formatting
                const previousDate = strAsDate(date);
                setInputValue(
                    previousDate ? formatDate(previousDate, display_format) : ''
                );
                if (focusCalendar) {
                    calendarRef.current?.focusDate(previousDate);
                }
            }
        },
        [inputValue, display_format, date, minDate, maxDate, disabledDates]
    );

    const clearSelection = useCallback(
        (e: React.MouseEvent<HTMLAnchorElement>) => {
            setInternalDate(undefined);
            inputRef.current?.focus();
            e.preventDefault();
            e.stopPropagation();
            if (reopen_calendar_on_clear) {
                setIsCalendarOpen(true);
            }
        },
        [reopen_calendar_on_clear]
    );

    const handleInputKeyDown = useCallback(
        (e: React.KeyboardEvent<HTMLInputElement>) => {
            if (['ArrowUp', 'ArrowDown', 'Enter'].includes(e.key)) {
                e.preventDefault();
                if (!isCalendarOpen) {
                    setIsCalendarOpen(true);
                }
                // Wait for calendar to mount before focusing
                requestAnimationFrame(() => parseUserInput(true));
            } else if (e.key === 'Tab') {
                parseUserInput();
            }
        },
        [isCalendarOpen, parseUserInput]
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
                        aria-labelledby={`${accessibleId}`}
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
                                inputRef.current = node;
                            }}
                            type="text"
                            id={accessibleId}
                            inputClassName="dash-datepicker-input dash-datepicker-end-date"
                            value={inputValue}
                            onChange={e => setInputValue(e.target?.value)}
                            onKeyDown={handleInputKeyDown}
                            placeholder={placeholder}
                            disabled={disabled}
                            dir={direction}
                            aria-label={placeholder}
                        />
                        {clearable && !disabled && !!date && (
                            <a
                                className="dash-datepicker-clear"
                                onClick={clearSelection}
                                aria-label="Clear date"
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
                            // Only focus if focus is not already on the input
                            if (document.activeElement !== inputRef.current) {
                                inputRef.current?.focus();
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
                            initialVisibleDate={initialMonth}
                            selectionStart={internalDate}
                            selectionEnd={internalDate}
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
                            onSelectionChange={(_, selection) => {
                                if (!selection) {
                                    return;
                                }
                                setInternalDate(selection);
                                if (!stay_open_on_select) {
                                    setIsCalendarOpen(false);
                                }
                            }}
                        />
                    </Popover.Content>
                </Popover.Portal>
            </Popover.Root>
        </div>
    );
};

export default DatePickerSingle;
