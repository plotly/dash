import React from 'react';
import {render, fireEvent} from '@testing-library/react';
import {CalendarMonth} from '../../../src/utils/calendar/CalendarMonth';
import {CalendarDirection} from '../../../src/types';

describe('CalendarMonth', () => {
    it('renders a calendar month with correct structure', () => {
        const {container} = render(<CalendarMonth year={2025} month={0} />);

        const table = container.querySelector('table');
        expect(table).toBeInTheDocument();

        // Should have 7 day-of-week headers
        const headers = container.querySelectorAll('thead th');
        expect(headers.length).toBeGreaterThanOrEqual(7);
    });

    describe('when showOutsideDays=false', () => {
        it.each([
            {
                month: 5, // June
                monthName: 'June',
                daysInMonth: 30,
                startsOnDay: 0, // Sunday
                expectedFirstIndex: 0,
                expectedEmptyCellsBefore: 0,
            },
            {
                month: 0, // January
                monthName: 'January',
                daysInMonth: 31,
                startsOnDay: 3, // Wednesday
                expectedFirstIndex: 3,
                expectedEmptyCellsBefore: 3,
            },
        ])(
            'renders $monthName 2025 with correct labeled and unlabeled cells',
            ({
                month,
                monthName,
                daysInMonth,
                expectedFirstIndex,
                expectedEmptyCellsBefore,
            }) => {
                const {container} = render(
                    <CalendarMonth
                        year={2025}
                        month={month}
                        firstDayOfWeek={0} // Sunday first
                        showOutsideDays={false}
                    />
                );

                const allCells = container.querySelectorAll('td');
                const cellTexts = Array.from(allCells).map(
                    td => td.textContent?.trim() || ''
                );
                const labeledCells = cellTexts.filter(text => text !== '');

                // All days in the month should be labeled in correct order
                expect(labeledCells.length).toBe(daysInMonth);
                const days = labeledCells.map(text => parseInt(text, 10));
                expect(days).toEqual(
                    Array.from({length: daysInMonth}, (_, i) => i + 1)
                );

                // First day should appear at expected position
                const firstDayIndex = cellTexts.findIndex(text => text === '1');
                expect(firstDayIndex).toBe(expectedFirstIndex);

                // Cells before first day should be unlabeled
                if (expectedEmptyCellsBefore > 0) {
                    expect(
                        cellTexts.slice(0, expectedEmptyCellsBefore)
                    ).toEqual(Array(expectedEmptyCellsBefore).fill(''));
                }

                // Cells after last day in the same week should be unlabeled
                const lastDayIndex = cellTexts.lastIndexOf(String(daysInMonth));
                const remainingInWeek = 6 - (lastDayIndex % 7);
                for (let i = 1; i <= remainingInWeek; i++) {
                    expect(cellTexts[lastDayIndex + i]).toBe('');
                }
            }
        );
    });

    it('shows outside day labels when showOutsideDays=true with Monday first', () => {
        // January 2025: starts on Wednesday (day 3)
        // With Monday as first day of week, we show: Mon Dec 30, Tue Dec 31, then Wed Jan 1
        const {container} = render(
            <CalendarMonth
                year={2025}
                month={0} // January
                firstDayOfWeek={1} // Monday first
                showOutsideDays={true}
            />
        );

        const allCells = container.querySelectorAll('td');
        const cellTexts = Array.from(allCells).map(
            td => td.textContent?.trim() || ''
        );

        const labeledCells = cellTexts.filter(text => text !== '');

        // First 2 cells should be December days (30, 31), then January 1
        expect(cellTexts[0]).toBe('30');
        expect(cellTexts[1]).toBe('31');

        // 3rd cell should be January 1
        expect(cellTexts[2]).toBe('1');

        // Verify January days continue in sequence
        expect(cellTexts[3]).toBe('2');
        expect(cellTexts[4]).toBe('3');
    });

    it('marks selected dates', () => {
        const selectedDates: Date[] = [
            new Date(2025, 0, 5),
            new Date(2025, 0, 10),
        ];

        const {container} = render(
            <CalendarMonth
                year={2025}
                month={0}
                selectedDates={selectedDates}
            />
        );

        const allCells = container.querySelectorAll('td');
        const selectedCells = Array.from(allCells).filter(td =>
            td.classList.contains('dash-datepicker-calendar-date-selected')
        );

        // Only the two specific dates should be selected (5th and 10th)
        expect(selectedCells.length).toBe(2);
    });

    it('marks highlighted dates with date range', () => {
        const highlightedDates: [Date, Date] = [
            new Date(2025, 0, 10),
            new Date(2025, 0, 15),
        ];

        const {container} = render(
            <CalendarMonth
                year={2025}
                month={0}
                highlightedDatesRange={highlightedDates}
            />
        );

        const allCells = container.querySelectorAll('td');
        const highlightedCells = Array.from(allCells).filter(td =>
            td.classList.contains('dash-datepicker-calendar-date-highlighted')
        );

        expect(highlightedCells.length).toBe(6); // Jan 10-15 = 6 days
    });

    it('handles undefined selectedDatesRange', () => {
        const {container} = render(
            <CalendarMonth year={2025} month={0} selectedDates={undefined} />
        );

        const allCells = container.querySelectorAll('td');
        const selectedCells = Array.from(allCells).filter(td =>
            td.classList.contains('dash-datepicker-calendar-date-selected')
        );

        expect(selectedCells.length).toBe(0);
    });

    it('handles undefined date props', () => {
        const {container} = render(
            <CalendarMonth
                year={2025}
                month={0}
                selectedDates={undefined}
                highlightedDatesRange={undefined}
            />
        );

        const table = container.querySelector('table');
        expect(table).toBeInTheDocument();
    });

    describe('RTL support', () => {
        it('reverses keyboard navigation for ArrowLeft/ArrowRight in RTL', () => {
            const mockOnDayFocused = jest.fn();

            render(
                <CalendarMonth
                    year={2025}
                    month={0}
                    onDayFocused={mockOnDayFocused}
                    direction={CalendarDirection.RightToLeft}
                    dateFocused={new Date(2025, 0, 15)}
                />
            );

            // Use document.activeElement to find the actually focused cell
            const focusedCell = document.activeElement as HTMLElement;
            expect(focusedCell?.tagName).toBe('TD');
            expect(focusedCell?.textContent).toBe('15');

            mockOnDayFocused.mockClear(); // Clear any initial focus calls

            // Press ArrowRight - in RTL this should go to January 14 (backwards)
            fireEvent.keyDown(focusedCell!, {key: 'ArrowRight'});
            expect(mockOnDayFocused).toHaveBeenLastCalledWith(
                new Date(2025, 0, 14)
            );

            mockOnDayFocused.mockClear();

            // Press ArrowLeft - in RTL this should go to January 16 (forwards)
            fireEvent.keyDown(focusedCell!, {key: 'ArrowLeft'});
            expect(mockOnDayFocused).toHaveBeenLastCalledWith(
                new Date(2025, 0, 16)
            );
        });

        it('keeps ArrowUp/ArrowDown unchanged in RTL', () => {
            const mockOnDayFocused = jest.fn();

            render(
                <CalendarMonth
                    year={2025}
                    month={0}
                    onDayFocused={mockOnDayFocused}
                    direction={CalendarDirection.RightToLeft}
                    dateFocused={new Date(2025, 0, 15)}
                />
            );

            const focusedCell = document.activeElement as HTMLElement;
            expect(focusedCell?.tagName).toBe('TD');
            expect(focusedCell?.textContent).toBe('15');

            mockOnDayFocused.mockClear(); // Clear any initial focus calls

            // ArrowDown should still go forward 1 week
            fireEvent.keyDown(focusedCell!, {key: 'ArrowDown'});
            expect(mockOnDayFocused).toHaveBeenLastCalledWith(
                new Date(2025, 0, 22)
            );

            mockOnDayFocused.mockClear();

            // ArrowUp should still go backward 1 week
            fireEvent.keyDown(focusedCell!, {key: 'ArrowUp'});
            expect(mockOnDayFocused).toHaveBeenLastCalledWith(
                new Date(2025, 0, 8)
            );
        });
    });
});
