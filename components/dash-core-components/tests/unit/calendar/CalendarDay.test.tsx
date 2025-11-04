import React from 'react';
import {render} from '@testing-library/react';
import CalendarDay from '../../../src/utils/calendar/CalendarDay';

describe('CalendarDay', () => {
    const renderDay = (props: React.ComponentProps<typeof CalendarDay>) => {
        const {container} = render(
            <table>
                <tbody>
                    <tr>
                        <CalendarDay {...props} />
                    </tr>
                </tbody>
            </table>
        );
        const td = container.querySelector('td');
        if (!td) {
            throw new Error('td element not rendered');
        }
        return td;
    };

    it('renders with correct label and inside/outside classes', () => {
        const insideDay = renderDay({
            date: new Date(2025, 0, 15),
            isOutside: false,
            showOutsideDays: true,
        });
        expect(insideDay.textContent).toBe('15');
        expect(
            insideDay.classList.contains('dash-datepicker-calendar-date-inside')
        ).toBe(true);
        expect(
            insideDay.classList.contains(
                'dash-datepicker-calendar-date-outside'
            )
        ).toBe(false);

        const outsideDay = renderDay({
            date: new Date(2024, 11, 31),
            isOutside: true,
            showOutsideDays: true,
        });
        expect(outsideDay.textContent).toBe('31');
        expect(
            outsideDay.classList.contains(
                'dash-datepicker-calendar-date-outside'
            )
        ).toBe(true);
        expect(
            outsideDay.classList.contains(
                'dash-datepicker-calendar-date-inside'
            )
        ).toBe(false);
    });

    it('marks disabled day with correct attributes', () => {
        const td = renderDay({
            date: new Date(2025, 0, 10),
            isOutside: false,
            showOutsideDays: true,
            isDisabled: true,
        });

        expect(
            td.classList.contains('dash-datepicker-calendar-date-disabled')
        ).toBe(true);
        expect(td.getAttribute('aria-disabled')).toBe('true');
        expect(td.getAttribute('tabIndex')).toBeNull();
    });

    it('hides label for outside days when showOutsideDays is false', () => {
        const td = renderDay({
            date: new Date(2024, 11, 31),
            isOutside: true,
            showOutsideDays: false,
        });

        expect(td.textContent).toBe('');
        expect(
            td.classList.contains('dash-datepicker-calendar-date-outside')
        ).toBe(true);
    });

    it('focuses element when isFocused is true', () => {
        const td = renderDay({
            date: new Date(2025, 0, 15),
            isOutside: false,
            showOutsideDays: true,
            isFocused: true,
        });

        expect(td).toBe(document.activeElement);
    });
});
