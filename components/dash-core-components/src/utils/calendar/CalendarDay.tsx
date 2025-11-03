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
    label: string;
    isOutside: boolean;
    isSelected?: boolean;
    isHighlighted?: boolean;
    isFocused?: boolean;
    isDisabled?: boolean;
};

const CalendarDay = ({
    label,
    isOutside,
    isSelected = false,
    isHighlighted = false,
    isFocused = false,
    isDisabled = false,
    className,
    ...passThruProps
}: CalendarDayProps): JSX.Element => {
    let extraClasses = '';
    if (isOutside) {
        extraClasses += ' dash-datepicker-calendar-date-outside';
    } else {
        extraClasses += ' dash-datepicker-calendar-date-inside';
    }
    if (isSelected && !(isOutside && !label)) {
        // does not apply this class to a blank cell in another month
        // (relevant when `number_of_months_shown > 1`)
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

    const filteredProps = isDisabled
        ? Object.fromEntries(
              Object.entries(passThruProps).filter(
                  ([key]) => !key.startsWith('on')
              )
          )
        : passThruProps;

    return (
        <td
            className={className}
            {...filteredProps}
            ref={ref}
            aria-disabled={isDisabled}
            tabIndex={isOutside || isDisabled ? undefined : 0}
        >
            <span>{label}</span>
        </td>
    );
};

export default CalendarDay;
