import React, {useMemo} from 'react';
import {formatDate} from './helpers';

const CalendarMonthHeader = (props: {
    year: number;
    month: number;
    monthFormat?: string;
}) => {
    const label = useMemo(() => {
        return formatDate(
            new Date(props.year, props.month, 1),
            props.monthFormat
        );
    }, [props]);

    return (
        <th colSpan={7} className="dash-datepicker-calendar-month-header">
            {label}
        </th>
    );
};

export default CalendarMonthHeader;
