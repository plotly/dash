import moment from 'moment';

/**
 * Creates a 2D array of Date objects representing a calendar month grid.
 * Always returns exactly 6 rows (weeks) to maintain consistent calendar height.
 */
export const createMonthGrid = (
    year: number,
    month: number,
    firstDayOfWeek: number,
    showOutsideDays = true
): (Date | null)[][] => {
    const firstDay = moment([year, month, 1]);
    const offset = (firstDay.day() - firstDayOfWeek + 7) % 7;
    const daysInMonth = firstDay.daysInMonth();
    const weeksNeeded = Math.ceil((offset + daysInMonth) / 7);
    const startDate = firstDay.clone().subtract(offset, 'days');

    const grid: (Date | null)[][] = [];

    for (let week = 0; week < weeksNeeded; week++) {
        grid.push(
            Array.from({length: 7}, (_, day) => {
                const date = startDate.clone().add(week * 7 + day, 'days');
                if (!showOutsideDays && date.month() !== month) {
                    return null;
                }
                return date.toDate();
            })
        );
    }

    // Pad with empty rows to always have 6 rows total
    while (grid.length < 6) {
        grid.push(Array.from({length: 7}, () => null));
    }

    return grid;
};
