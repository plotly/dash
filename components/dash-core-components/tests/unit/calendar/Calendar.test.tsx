import React from 'react';
import {render, waitFor, act} from '@testing-library/react';
import Calendar from '../../../src/utils/calendar/Calendar';
import {CalendarDirection} from '../../../src/types';

// Mock LoadingElement to avoid Dash context issues in tests
jest.mock('../../../src/utils/_LoadingElement', () => {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const React = require('react');
    return function LoadingElement({
        children,
    }: {
        children: (props: any) => React.ReactNode;
    }) {
        return children({});
    };
});

// Helper to count cells with a specific CSS class
const countCellsWithClass = (
    container: HTMLElement,
    className: string
): number => {
    const allCells = container.querySelectorAll('td');
    return Array.from(allCells).filter(td => td.classList.contains(className))
        .length;
};

describe('Calendar', () => {
    let mockOnSelectionChange: jest.Mock;

    beforeEach(() => {
        mockOnSelectionChange = jest.fn();
    });

    it('renders a calendar', () => {
        const {container} = render(
            <Calendar onSelectionChange={mockOnSelectionChange} />
        );

        const calendarWrapper = container.querySelector(
            '.dash-datepicker-calendar-wrapper'
        );
        expect(calendarWrapper).toBeInTheDocument();
    });

    it('marks disabled dates correctly', () => {
        const disabledDates = [new Date(2025, 0, 10), new Date(2025, 0, 15)];

        const {container} = render(
            <Calendar
                onSelectionChange={mockOnSelectionChange}
                initialVisibleDate={new Date(2025, 0, 1)}
                disabledDates={disabledDates}
            />
        );

        expect(
            countCellsWithClass(
                container,
                'dash-datepicker-calendar-date-disabled'
            )
        ).toBeGreaterThan(0);
    });

    it('marks selected dates from selectionStart and selectionEnd', () => {
        const {container} = render(
            <Calendar
                onSelectionChange={mockOnSelectionChange}
                initialVisibleDate={new Date(2025, 0, 1)}
                selectionStart={new Date(2025, 0, 10)}
                selectionEnd={new Date(2025, 0, 15)}
            />
        );

        // Should have 2 selected days (only the start and end dates, not the dates in between)
        expect(
            countCellsWithClass(
                container,
                'dash-datepicker-calendar-date-selected'
            )
        ).toBe(2);
    });

    it('marks highlighted dates from highlightStart and highlightEnd', () => {
        const {container} = render(
            <Calendar
                onSelectionChange={mockOnSelectionChange}
                initialVisibleDate={new Date(2025, 0, 1)}
                highlightStart={new Date(2025, 0, 5)}
                highlightEnd={new Date(2025, 0, 10)}
            />
        );

        // Should have 6 highlighted days (Jan 5-10 inclusive)
        expect(
            countCellsWithClass(
                container,
                'dash-datepicker-calendar-date-highlighted'
            )
        ).toBe(6);
    });

    it('handles single date selection', () => {
        const {container} = render(
            <Calendar
                onSelectionChange={mockOnSelectionChange}
                initialVisibleDate={new Date(2025, 0, 1)}
                selectionStart={new Date(2025, 0, 15)}
            />
        );

        // Should have 1 selected day
        expect(
            countCellsWithClass(
                container,
                'dash-datepicker-calendar-date-selected'
            )
        ).toBe(1);
    });

    it.each([
        {
            description: 'default format (YYYY)',
            date: new Date(1997, 4, 10),
            monthFormat: undefined,
            expectedYear: '1997',
            expectedMonth: /May/,
        },
        {
            description: 'YY format',
            date: new Date(1997, 4, 10),
            monthFormat: 'MMMM YY',
            expectedYear: '97',
            expectedMonth: /May/,
        },
        {
            description: 'YYYY format with January',
            date: new Date(2023, 0, 15),
            monthFormat: undefined,
            expectedYear: '2023',
            expectedMonth: /January/,
        },
    ])(
        'formats year and month according to month_format: $description',
        ({date, monthFormat, expectedYear, expectedMonth}) => {
            const {container} = render(
                <Calendar
                    onSelectionChange={mockOnSelectionChange}
                    initialVisibleDate={date}
                    monthFormat={monthFormat}
                />
            );

            const yearInput = container.querySelector(
                '.dash-input-element'
            ) as HTMLInputElement;
            expect(yearInput.value).toBe(expectedYear);

            const monthButton = container.querySelector(
                '.dash-dropdown-trigger'
            );
            expect(monthButton?.textContent).toMatch(expectedMonth);
        }
    );

    it('parses year input with moment.js rules (1-digit, 2-digit, 4-digit)', async () => {
        const mockOnSelectionChange = jest.fn();

        const {container} = render(
            <Calendar
                onSelectionChange={mockOnSelectionChange}
                initialVisibleDate={new Date(2000, 0, 1)}
            />
        );

        const yearInput = container.querySelector(
            '.dash-input-element'
        ) as HTMLInputElement;
        expect(yearInput.value).toBe('2000');

        // Test 2-digit year: "97" → 1997
        act(() => {
            yearInput.value = '97';
            yearInput.dispatchEvent(new Event('change', {bubbles: true}));
        });
        await waitFor(() => expect(yearInput.value).toBe('97'), {
            timeout: 1000,
        });

        // Test 4-digit year: "2025" → 2025
        act(() => {
            yearInput.value = '2025';
            yearInput.dispatchEvent(new Event('change', {bubbles: true}));
        });
        await waitFor(() => expect(yearInput.value).toBe('2025'), {
            timeout: 1000,
        });

        // Test single-digit year: "5" → 2005
        act(() => {
            yearInput.value = '5';
            yearInput.dispatchEvent(new Event('change', {bubbles: true}));
        });
        await waitFor(() => expect(yearInput.value).toBe('5'), {timeout: 1000});
    });

    it.each([
        {
            description: 'selected date when visible in current month',
            visibleMonth: new Date(2020, 0, 1),
            selectedDate: new Date(2020, 0, 23),
            expectedFocusedDay: '23',
        },
        {
            description: 'selected date even when not initially visible',
            visibleMonth: new Date(2020, 0, 1),
            selectedDate: new Date(2025, 9, 17),
            expectedFocusedDay: '17', // Calendar switches to October 2025
        },
        {
            description: 'first day when no date is selected',
            visibleMonth: new Date(2020, 0, 1),
            selectedDate: undefined,
            expectedFocusedDay: '1',
        },
    ])(
        'focuses $description',
        ({visibleMonth, selectedDate, expectedFocusedDay}) => {
            const ref = React.createRef<any>();
            render(
                <Calendar
                    ref={ref}
                    onSelectionChange={mockOnSelectionChange}
                    initialVisibleDate={visibleMonth}
                    selectionStart={selectedDate}
                />
            );

            // Imperatively focus the appropriate date
            const dateToFocus = selectedDate || visibleMonth;
            act(() => {
                ref.current?.focusDate(dateToFocus);
            });

            const focusedElement = document.activeElement;
            expect(focusedElement?.tagName).toBe('TD');
            expect(focusedElement?.textContent).toBe(expectedFocusedDay);
        }
    );

    describe('RTL support', () => {
        it('applies RTL directionality to calendar container', () => {
            const {container: rtlContainer} = render(
                <Calendar
                    onSelectionChange={mockOnSelectionChange}
                    direction={CalendarDirection.RightToLeft}
                />
            );

            const {container: ltrContainer} = render(
                <Calendar
                    onSelectionChange={mockOnSelectionChange}
                    direction={CalendarDirection.LeftToRight}
                />
            );

            // dir attribute should be on calendar-container, not wrapper (to avoid reversing controls)
            const rtlContainer_div = rtlContainer.querySelector(
                '.dash-datepicker-calendar-container'
            );
            const ltrContainer_div = ltrContainer.querySelector(
                '.dash-datepicker-calendar-container'
            );

            expect(rtlContainer_div).toHaveAttribute('dir', 'rtl');
            expect(ltrContainer_div).toHaveAttribute('dir', 'ltr');
        });
    });
});
