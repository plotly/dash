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

        expect(td).toBeInTheDocument();
        expect(td).toHaveClass('dash-datepicker-calendar-padding');
        expect(td).not.toHaveClass('dash-datepicker-calendar-date-inside');
        expect(td).not.toHaveClass('dash-datepicker-calendar-date-outside');
        expect(td).toHaveTextContent('');
    });
});
