import moment from 'moment';

/**
 * Creates a 2D array of Date objects representing a calendar month grid.
 * @param year - The year
 * @param month - The month (0-11)
 * @param firstDayOfWeek - The first day of week (0=Sunday, 1=Monday, etc.)
 * @returns 2D array where each inner array is a week of Date objects
 */
export const createMonthGrid = (
    year: number,
    month: number,
    firstDayOfWeek: number
): Date[][] => {
    const firstDay = moment([year, month, 1]);
    const offset = (firstDay.day() - firstDayOfWeek + 7) % 7;
    const totalCells = Math.ceil((offset + firstDay.daysInMonth()) / 7) * 7;
    const startDate = firstDay.clone().subtract(offset, 'days');

    const grid: Date[][] = [];
    for (let i = 0; i < totalCells; i += 7) {
        grid.push(
            Array.from({length: 7}, (_, j) =>
                startDate.clone().add(i + j, 'days').toDate()
            )
        );
    }

    return grid;
};
