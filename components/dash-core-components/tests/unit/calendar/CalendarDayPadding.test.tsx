import React from 'react';
import {render} from '@testing-library/react';
import CalendarDayPadding from '../../../src/utils/calendar/CalendarDayPadding';

describe('CalendarDayPadding', () => {
    it('renders padding cell with correct class and empty content', () => {
        const {container} = render(
            <table>
                <tbody>
                    <tr>
                        <CalendarDayPadding />
                    </tr>
                </tbody>
            </table>
        );
        const td = container.querySelector('td');
        if (!td) {
            throw new Error('td element not rendered');
        }

        expect(td.classList.contains('dash-datepicker-calendar-padding')).toBe(
            true
        );
        expect(
            td.classList.contains('dash-datepicker-calendar-date-inside')
        ).toBe(false);
        expect(
            td.classList.contains('dash-datepicker-calendar-date-outside')
        ).toBe(false);
        expect(td.textContent).toBe('');
    });
});
