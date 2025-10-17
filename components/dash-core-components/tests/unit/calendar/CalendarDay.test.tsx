import React from 'react';
import {render} from '@testing-library/react';
import CalendarDay from '../../../src/utils/calendar/CalendarDay';

describe('CalendarDay', () => {
    it('renders a basic minimal calendar day', () => {
        const {container} = render(
            <table>
                <tbody>
                    <tr>
                        <CalendarDay label="test" isOutside={false} />
                    </tr>
                </tbody>
            </table>
        );

        const td = container.querySelector('td');
        expect(td).toBeInTheDocument();
        expect(td?.textContent).toBe('test');
        expect(td?.classList.contains('dash-datepicker-calendar-date-inside')).toBe(true);
    });

    it('renders outside day with correct className', () => {
        const {container} = render(
            <table>
                <tbody>
                    <tr>
                        <CalendarDay label="31" isOutside={true} />
                    </tr>
                </tbody>
            </table>
        );

        const td = container.querySelector('td');
        expect(td).toBeInTheDocument();
        expect(td?.textContent).toBe('31');
        expect(td?.classList.contains('dash-datepicker-calendar-date-outside')).toBe(true);
        expect(td?.classList.contains('dash-datepicker-calendar-date-inside')).toBe(false);
    });

    it('prevents interaction with disabled calendar day', () => {
        const mockOnClick = jest.fn();

        const {container} = render(
            <table>
                <tbody>
                    <tr>
                        <CalendarDay label="10" isOutside={false} isDisabled={true} onClick={mockOnClick} />
                    </tr>
                </tbody>
            </table>
        );

        const td = container.querySelector('td');
        expect(td).toBeInTheDocument();
        expect(td?.classList.contains('dash-datepicker-calendar-date-disabled')).toBe(true);
        expect(td?.getAttribute('aria-disabled')).toBe('true');

        // Click the disabled day and verify the event is prevented
        td?.click();
        expect(mockOnClick).not.toHaveBeenCalled();

        // Verify disabled day has no tabIndex (cannot be focused via keyboard)
        expect(td?.getAttribute('tabIndex')).toBeNull();

        // Try to focus the element and verify it doesn't receive focus
        td?.focus();
        expect(document.activeElement).not.toBe(td);
    });

    it('focuses the element when isFocused is true', () => {
        const {container} = render(
            <table>
                <tbody>
                    <tr>
                        <CalendarDay label="15" isOutside={false} isFocused={true} />
                    </tr>
                </tbody>
            </table>
        );

        const td = container.querySelector('td');
        expect(td).toBe(document.activeElement);
    });
});
