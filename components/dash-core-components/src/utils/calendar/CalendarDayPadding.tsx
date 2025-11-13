import React from 'react';

/*
 * Renders an "empty" cell in a calendar month, representing days that fall
 * outside the month
 */
const CalendarDayPadding = (): JSX.Element => {
    return (
        <td className="dash-datepicker-calendar-padding">
            <span></span>
        </td>
    );
};

export default CalendarDayPadding;
