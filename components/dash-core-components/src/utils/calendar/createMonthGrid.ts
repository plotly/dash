import {getDay, getDaysInMonth, addDays, getMonth, type Day} from 'date-fns';

/**
 * Creates a 2D array of Date objects representing a calendar month grid.
 * Always returns exactly 6 rows (weeks) to maintain consistent calendar height.
 */
export const createMonthGrid = (
    year: number,
    month: number,
    firstDayOfWeek: Day,
    showOutsideDays = true
): (Date | null)[][] => {
    const firstDay = new Date(year, month, 1);
    const offset = (getDay(firstDay) - firstDayOfWeek + 7) % 7;
    const startDate = addDays(firstDay, -offset);
    const weeksNeeded = Math.ceil((offset + getDaysInMonth(firstDay)) / 7);

    return Array.from({length: 6}, (_, week) =>
        Array.from({length: 7}, (_, day) => {
            if (week >= weeksNeeded) {
                return null;
            }

            const date = addDays(startDate, week * 7 + day);
            return showOutsideDays || getMonth(date) === month ? date : null;
        })
    );
};
