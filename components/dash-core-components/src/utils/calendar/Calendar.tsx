import React, {
    useCallback,
    useEffect,
    useImperativeHandle,
    useMemo,
    useRef,
    useState,
    forwardRef,
} from 'react';
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
import {
    getMonthOptions,
    formatYear,
    parseYear,
    isDateInRange,
    isSameDay,
} from './helpers';

export type CalendarHandle = {
    focusDate: (date?: Date) => void;
    setVisibleDate: (date: Date) => void;
};

type CalendarProps = {
    onSelectionChange: (selectionStart: Date, selectionEnd?: Date) => void;
    selectionStart?: Date;
    selectionEnd?: Date;
    highlightStart?: Date;
    highlightEnd?: Date;
    initialVisibleDate?: Date;
    minDateAllowed?: Date;
    maxDateAllowed?: Date;
    disabledDates?: Date[];
    firstDayOfWeek?: DayOfWeek;
    showOutsideDays?: boolean;
    monthFormat?: string;
    calendarOrientation?: 'vertical' | 'horizontal';
    numberOfMonthsShown?: number;
    daySize?: number;
    direction?: CalendarDirection;
};

type CalendarPropsWithRef = CalendarProps & {
    forwardedRef?: React.Ref<CalendarHandle>;
};

const CalendarComponent = ({
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
    forwardedRef,
}: CalendarPropsWithRef) => {
    const [activeYear, setActiveYear] = useState(() =>
        initialVisibleDate.getFullYear()
    );
    const [activeMonth, setActiveMonth] = useState(() =>
        initialVisibleDate.getMonth()
    );

    const [focusedDate, setFocusedDate] = useState<Date>();
    const [highlightedDates, setHighlightedDates] = useState<[Date, Date]>();
    const calendarContainerRef = useRef(document.createElement('div'));
    const scrollAccumulatorRef = useRef(0);
    const prevFocusedDateRef = useRef(focusedDate);

    const displayYear = useMemo(() => {
        const formatted = formatYear(activeYear, monthFormat);
        return parseInt(formatted, 10);
    }, [activeYear, monthFormat]);

    useImperativeHandle(forwardedRef, () => ({
        focusDate: (date = moment([activeYear, activeMonth, 1]).toDate()) => {
            setFocusedDate(date);
        },
        setVisibleDate: (date: Date) => {
            setActiveMonth(date.getMonth());
            setActiveYear(date.getFullYear());
        },
    }));

    useEffect(() => {
        // Syncs activeMonth/activeYear to focusedDate when focusedDate changes
        if (!focusedDate) {
            return;
        }
        if (focusedDate.getTime() === prevFocusedDateRef.current?.getTime()) {
            return;
        }
        prevFocusedDateRef.current = focusedDate;

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
        if (highlightStart && highlightEnd) {
            setHighlightedDates([highlightStart, highlightEnd]);
        } else if (highlightStart) {
            setHighlightedDates([highlightStart, highlightStart]);
        } else {
            setHighlightedDates(undefined);
        }
    }, [highlightStart, highlightEnd]);

    useEffect(() => {
        if (selectionStart && selectionEnd) {
            setHighlightedDates([selectionStart, selectionEnd]);
        }
    }, [selectionStart, selectionEnd]);

    const selectedDates = useMemo((): Date[] => {
        return [selectionStart, selectionEnd].filter(
            (d): d is Date => d !== undefined
        );
    }, [selectionStart, selectionEnd]);

    const handleSelectionStart = useCallback(
        (date: Date) => {
            if (!selectionStart || selectionEnd) {
                // No selection yet, or previous selection is complete → start new selection
                setHighlightedDates(undefined);
                onSelectionChange(date, undefined);
            }
        },
        [selectionStart, selectionEnd, onSelectionChange]
    );

    const handleSelectionEnd = useCallback(
        (date: Date) => {
            // Complete the selection with an end date
            if (selectionStart && !selectionEnd) {
                // Incomplete selection exists (range picker mid-selection)
                if (!isSameDay(selectionStart, date)) {
                    onSelectionChange(selectionStart, date);
                }
            } else {
                // Complete selection exists or a single date was chosen
                onSelectionChange(date, date);
            }
        },
        [selectionStart, selectionEnd, onSelectionChange]
    );

    const handleDaysHighlighted = useCallback(
        (date: Date) => {
            if (selectionStart && selectionEnd) {
                setHighlightedDates([selectionStart, selectionEnd]);
            } else if (selectionStart && !selectionEnd) {
                setHighlightedDates([selectionStart, date]);
            } else {
                setHighlightedDates([date, date]);
            }
        },
        [selectionStart, selectionEnd]
    );

    const handleDayFocused = useCallback(
        (date: Date) => {
            setFocusedDate(date);
            // When navigating with keyboard during range selection,
            // highlight the range from start to focused date
            if (selectionStart && !selectionEnd) {
                setHighlightedDates([selectionStart, date]);
            }
        },
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

    const changeMonthBy = useCallback(
        (months: number) => {
            const currentDate = moment([activeYear, activeMonth, 1]);

            // In RTL mode, directions are reversed
            const actualMonths =
                direction === CalendarDirection.RightToLeft ? -months : months;

            const newDate = currentDate.clone().add(actualMonths, 'month');
            const newMonthStart = newDate.toDate();

            if (isDateInRange(newMonthStart, minDateAllowed, maxDateAllowed)) {
                setActiveYear(newDate.year());
                setActiveMonth(newDate.month());
            }
        },
        [activeYear, activeMonth, minDateAllowed, maxDateAllowed, direction]
    );

    const handleWheel = useCallback(
        (e: WheelEvent) => {
            e.preventDefault();

            // Accumulate scroll delta until threshold is reached, then change the active month
            // This respects OS scroll speed settings and works well with trackpads
            const threshold = 100; // Adjust this to control sensitivity

            scrollAccumulatorRef.current += e.deltaY;

            if (Math.abs(scrollAccumulatorRef.current) >= threshold) {
                const offset = scrollAccumulatorRef.current > 0 ? 1 : -1;
                changeMonthBy(offset);
                scrollAccumulatorRef.current = 0; // Reset accumulator after month change
            }
        },
        [changeMonthBy]
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

    const canChangeMonthBy = useCallback(
        (months: number) => {
            const currentDate = moment([activeYear, activeMonth, 1]);
            const targetMonth = currentDate
                .clone()
                .add(months, 'month')
                .toDate();

            return isDateInRange(targetMonth, minDateAllowed, maxDateAllowed);
        },
        [activeYear, activeMonth, minDateAllowed, maxDateAllowed]
    );

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
                    onClick={() => changeMonthBy(-1)}
                    disabled={!canChangeMonthBy(-1)}
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
                    min={minDateAllowed?.getFullYear()}
                    max={maxDateAllowed?.getFullYear()}
                    setProps={({value}) => {
                        const parsed = parseYear(String(value));
                        if (parsed !== undefined) {
                            setActiveYear(parsed);
                        }
                    }}
                />
                <button
                    className="dash-datepicker-month-nav"
                    onClick={() => changeMonthBy(1)}
                    disabled={!canChangeMonthBy(1)}
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
                            onDayFocused={handleDayFocused}
                            selectedDates={selectedDates}
                            onSelectionStart={handleSelectionStart}
                            onSelectionEnd={handleSelectionEnd}
                            highlightedDatesRange={highlightedDates}
                            onDaysHighlighted={handleDaysHighlighted}
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

const Calendar = forwardRef<CalendarHandle, CalendarProps>((props, ref) => {
    return <CalendarComponent {...props} forwardedRef={ref} />;
});

Calendar.displayName = 'Calendar';

export default Calendar;
