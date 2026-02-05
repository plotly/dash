import React, {
    DetailedHTMLProps,
    TdHTMLAttributes,
    useEffect,
    useRef,
} from 'react';

type CalendarDayProps = DetailedHTMLProps<
    TdHTMLAttributes<HTMLTableCellElement>,
    HTMLTableCellElement
> & {
    date: Date;
    isOutside: boolean;
    showOutsideDays: boolean;
    isSelected?: boolean;
    isHighlighted?: boolean;
    isFocused?: boolean;
    isDisabled?: boolean;
};

const CalendarDay = ({
    date,
    isOutside,
    showOutsideDays,
    isSelected = false,
    isHighlighted = false,
    isFocused = false,
    isDisabled = false,
    className,
    ...passThruProps
}: CalendarDayProps): JSX.Element => {
    // Compute label: show day number unless it's an outside day and we're not showing outside days
    const label = !showOutsideDays && isOutside ? '' : String(date.getDate());

    let extraClasses = '';

    if (isOutside) {
        extraClasses += ' dash-datepicker-calendar-date-outside';
    } else {
        extraClasses += ' dash-datepicker-calendar-date-inside';
    }

    if (isSelected) {
        extraClasses += ' dash-datepicker-calendar-date-selected';
    }
    if (isHighlighted) {
        extraClasses += ' dash-datepicker-calendar-date-highlighted';
    }
    if (isDisabled) {
        extraClasses += ' dash-datepicker-calendar-date-disabled';
    }
    className = (className ?? '') + extraClasses;

    const ref = useRef(document.createElement('td'));

    useEffect(() => {
        if (isFocused) {
            ref.current.focus();
        }
    }, [isFocused]);

    return (
        <td
            className={className}
            {...passThruProps}
            ref={ref}
            aria-disabled={isDisabled}
            tabIndex={isOutside || isDisabled ? undefined : 0}
        >
            <span>{label}</span>
        </td>
    );
};

export default CalendarDay;
