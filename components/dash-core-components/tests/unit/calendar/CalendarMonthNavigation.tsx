import React, {createRef} from 'react';
import {render, act} from '@testing-library/react';
import '@testing-library/jest-dom';
import Calendar, {CalendarHandle} from '../../../src/utils/calendar/Calendar';

describe('Calendar month visibility when calling setVisibleDate', () => {
    const calendarRef = createRef<CalendarHandle>();

    function getDisplayedMonths() {
        // Find all month headers in the calendar
        const monthHeaders = Array.from(
            document.querySelectorAll('.dash-datepicker-calendar-month-header')
        );
        return monthHeaders.map(header => header.textContent);
    }

    function renderCalendar(date: string, numberOfMonthsShown: number) {
        return render(
            <Calendar
                ref={calendarRef}
                initialVisibleDate={new Date(date)}
                numberOfMonthsShown={numberOfMonthsShown}
                monthFormat="MMMM YYYY"
                onSelectionChange={() => null}
            />
        );
    }

    describe('Calendar months start centered around initialVisibleDate', () => {
        test('shows current & next month when numberOfMonthsShown=2', () => {
            renderCalendar('2024-06-01', 2);
            expect(getDisplayedMonths()).toEqual(['June 2024', 'July 2024']);
        });

        test('shows previous, current, and next months when numberOfMonthsShown=3', () => {
            renderCalendar('2024-06-01', 3);
            expect(getDisplayedMonths()).toEqual([
                'May 2024',
                'June 2024',
                'July 2024',
            ]);
        });

        test('shows previous, current, and next 2 months when numberOfMonthsShown=4', () => {
            renderCalendar('2024-06-01', 4);
            expect(getDisplayedMonths()).toEqual([
                'May 2024',
                'June 2024',
                'July 2024',
                'August 2024',
            ]);
        });
    });

    describe('calendar stays static when navigating to already-displayed dates', () => {
        test('does not re-order displayed months (numberOfMonthsShown=2)', () => {
            renderCalendar('2024-06-01', 2);
            const expectedCalendarMonths = ['June 2024', 'July 2024'];

            // Navigate to second visible month (July)
            act(() => {
                calendarRef.current?.setVisibleDate(new Date('2024-07-23'));
            });

            expect(getDisplayedMonths()).toEqual(expectedCalendarMonths);

            // Navigate to first visible month (June)
            act(() => {
                calendarRef.current?.setVisibleDate(new Date('2024-06-15'));
            });

            expect(getDisplayedMonths()).toEqual(expectedCalendarMonths);
        });

        test('does not re-order displayed months (numberOfMonthsShown=3)', () => {
            renderCalendar('2024-06-01', 3);
            const expectedCalendarMonths = [
                'May 2024',
                'June 2024',
                'July 2024',
            ];

            // Navigate to first visible month (May)
            act(() => {
                calendarRef.current?.setVisibleDate(new Date('2024-05-15'));
            });

            expect(getDisplayedMonths()).toEqual(expectedCalendarMonths);

            // Navigate to last visible month (July)
            act(() => {
                calendarRef.current?.setVisibleDate(new Date('2024-07-23'));
            });

            expect(getDisplayedMonths()).toEqual(expectedCalendarMonths);
        });

        test('does not re-order displayed months (numberOfMonthsShown=4)', () => {
            renderCalendar('2024-06-01', 4);
            const expectedCalendarMonths = [
                'May 2024',
                'June 2024',
                'July 2024',
                'August 2024',
            ];

            // Navigate to middle visible month (June)
            act(() => {
                calendarRef.current?.setVisibleDate(new Date('2024-06-15'));
            });

            expect(getDisplayedMonths()).toEqual(expectedCalendarMonths);

            // Navigate to another middle visible month (July)
            act(() => {
                calendarRef.current?.setVisibleDate(new Date('2024-07-23'));
            });

            expect(getDisplayedMonths()).toEqual(expectedCalendarMonths);
        });
    });

    describe('forward navigation to a non-visible month', () => {
        test('shows target month as last visible month (numberOfMonthsShown=2)', () => {
            renderCalendar('2024-06-01', 2);

            act(() => {
                calendarRef.current?.setVisibleDate(new Date('2024-08-15'));
            });

            expect(getDisplayedMonths()).toEqual(['July 2024', 'August 2024']);
        });

        test('shows target month as last visible month (numberOfMonthsShown=3)', () => {
            renderCalendar('2024-06-01', 3);

            act(() => {
                calendarRef.current?.setVisibleDate(new Date('2024-09-15'));
            });

            expect(getDisplayedMonths()).toEqual([
                'July 2024',
                'August 2024',
                'September 2024',
            ]);
        });

        test('shows target month as last visible month (numberOfMonthsShown=4)', () => {
            renderCalendar('2024-08-01', 4);

            act(() => {
                calendarRef.current?.setVisibleDate(new Date('2025-01-17'));
            });

            expect(getDisplayedMonths()).toEqual([
                'October 2024',
                'November 2024',
                'December 2024',
                'January 2025',
            ]);
        });
    });

    describe('backward navigation to non-visible month', () => {
        test('shows target month as first visible month (numberOfMonthsShown=2)', () => {
            renderCalendar('2024-06-01', 2);

            act(() => {
                calendarRef.current?.setVisibleDate(new Date('2023-12-10'));
            });

            expect(getDisplayedMonths()).toEqual([
                'December 2023',
                'January 2024',
            ]);
        });
    });
});
