import React from 'react';
import {render, waitFor, fireEvent} from '@testing-library/react';
import DatePickerSingle from '../../../src/fragments/DatePickerSingle';
import {CalendarDirection} from '../../../src/types';

describe('DatePickerSingle', () => {
    it('renders a date picker', () => {
        const mockSetProps = jest.fn();

        const {container, unmount} = render(
            <DatePickerSingle setProps={mockSetProps} />
        );

        const datepicker = container.querySelector('.dash-datepicker');
        expect(datepicker).toBeInTheDocument();
        
        unmount();
    });

    it('marks disabled days correctly', async () => {
        const mockSetProps = jest.fn();
        const disabledDays = ['2025-01-10', '2025-01-15'];

        const {container, unmount} = render(
            <DatePickerSingle
                setProps={mockSetProps}
                initial_visible_month="2025-01-01"
                disabled_days={disabledDays}
            />
        );

        // Click the trigger to open the calendar
        const trigger = container.querySelector('.dash-datepicker-input-wrapper');
        trigger?.dispatchEvent(new MouseEvent('click', {bubbles: true}));

        // Wait for calendar to render
        await waitFor(() => {
            const allDays = container.querySelectorAll('td');
            expect(allDays.length).toBeGreaterThan(0);
        });

        const allDays = container.querySelectorAll('td');
        const disabledDays_rendered = Array.from(allDays).filter(td =>
            td.classList.contains('dash-datepicker-calendar-date-disabled')
        );

        expect(disabledDays_rendered.length).toBeGreaterThan(0);
        
        unmount();
    });

    it('displays date in custom display_format on initial mount', () => {
        const mockSetProps = jest.fn();

        // Render with a pre-selected date and custom format
        const {container, unmount} = render(
            <DatePickerSingle
                setProps={mockSetProps}
                display_format="MM DD YY"
                date="2025-10-17"
            />
        );

        // Check that input shows the date in custom format immediately on mount
        const input = container.querySelector('.dash-datepicker-input') as HTMLInputElement;
        expect(input.value).toBe('10 17 25'); // MM DD YY format, not YYYY-MM-DD

        unmount();
    });

    it('displays date in custom display_format after blur', async () => {
        const mockSetProps = jest.fn();

        // Render with a pre-selected date and custom format
        const {container, unmount} = render(
            <DatePickerSingle
                setProps={mockSetProps}
                display_format="MM/DD/YYYY"
                date="2025-01-15"
            />
        );

        // Check that input shows the date in custom format
        const input = container.querySelector('.dash-datepicker-input') as HTMLInputElement;
        expect(input.value).toBe('01/15/2025'); // MM/DD/YYYY format

        // Blur the input to trigger sendInputAsDate
        fireEvent.blur(input);

        // Wait for any state updates
        await waitFor(() => {
            const inputAfterBlur = container.querySelector('.dash-datepicker-input') as HTMLInputElement;
            // Should still be in custom format after blur
            expect(inputAfterBlur.value).toBe('01/15/2025');
        });

        unmount();
    });

    it('defaults to YYYY-MM-DD format when no display_format provided', async () => {
        const mockSetProps = jest.fn();

        // Render with a pre-selected date and no display_format
        const {container, unmount} = render(
            <DatePickerSingle
                setProps={mockSetProps}
                date="2025-01-10"
            />
        );

        // Check that input shows the date in default YYYY-MM-DD format
        const input = container.querySelector('.dash-datepicker-input') as HTMLInputElement;
        expect(input.value).toBe('2025-01-10'); // YYYY-MM-DD format

        // Blur the input
        fireEvent.blur(input);

        // Wait for any state updates
        await waitFor(() => {
            const inputAfterBlur = container.querySelector('.dash-datepicker-input') as HTMLInputElement;
            // Should still be in default format after blur
            expect(inputAfterBlur.value).toBe('2025-01-10');
        });

        unmount();
    });

    describe('RTL support', () => {
        it('applies directionality based on is_RTL prop', () => {
            const mockSetProps = jest.fn();

            const {container: rtlContainer, unmount: unmountRtl} = render(
                <DatePickerSingle setProps={mockSetProps} is_RTL={true} />
            );

            const {container: ltrContainer, unmount: unmountLtr} = render(
                <DatePickerSingle setProps={mockSetProps} is_RTL={false} />
            );

            const {container: defaultContainer, unmount: unmountDefault} = render(
                <DatePickerSingle setProps={mockSetProps} />
            );

            // dir attribute should be on input element
            expect(rtlContainer.querySelector('.dash-datepicker-input'))
                .toHaveAttribute('dir', CalendarDirection.RightToLeft);
            expect(ltrContainer.querySelector('.dash-datepicker-input'))
                .toHaveAttribute('dir', CalendarDirection.LeftToRight);
            expect(defaultContainer.querySelector('.dash-datepicker-input'))
                .toHaveAttribute('dir', CalendarDirection.LeftToRight);

            unmountRtl();
            unmountLtr();
            unmountDefault();
        });
    });
});
