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
        return container.querySelector('td')!;
    };

    it('renders with correct label and inside/outside classes', () => {
        const insideDay = renderDay({
            date: new Date(2025, 0, 15),
            isOutside: false,
            showOutsideDays: true,
        });
        expect(insideDay).toHaveTextContent('15');
        expect(insideDay).toHaveClass('dash-datepicker-calendar-date-inside');
        expect(insideDay).not.toHaveClass(
            'dash-datepicker-calendar-date-outside'
        );

        const outsideDay = renderDay({
            date: new Date(2024, 11, 31),
            isOutside: true,
            showOutsideDays: true,
        });
        expect(outsideDay).toHaveTextContent('31');
        expect(outsideDay).toHaveClass('dash-datepicker-calendar-date-outside');
        expect(outsideDay).not.toHaveClass(
            'dash-datepicker-calendar-date-inside'
        );
    });

    it('marks disabled day with correct attributes', () => {
        const td = renderDay({
            date: new Date(2025, 0, 10),
            isOutside: false,
            showOutsideDays: true,
            isDisabled: true,
        });

        expect(td).toHaveClass('dash-datepicker-calendar-date-disabled');
        expect(td).toHaveAttribute('aria-disabled', 'true');
        expect(td).not.toHaveAttribute('tabIndex');
    });

    it('hides label for outside days when showOutsideDays is false', () => {
        const td = renderDay({
            date: new Date(2024, 11, 31),
            isOutside: true,
            showOutsideDays: false,
        });

        expect(td).toHaveTextContent('');
        expect(td).toHaveClass('dash-datepicker-calendar-date-outside');
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
