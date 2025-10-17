import {createMonthGrid} from '../../../src/utils/calendar/createMonthGrid';

describe('createMonthGrid', () => {
    it('creates grid with correct dimensions', () => {
        const grid = createMonthGrid(2025, 0, 0); // January 2025, Sunday first

        // Should have complete weeks (4-6 rows, 7 columns each)
        expect(grid.length).toBeGreaterThanOrEqual(4);
        expect(grid.length).toBeLessThanOrEqual(6);
        
        grid.forEach(week => {
            expect(week.length).toBe(7);
        });
    });

    it('has consecutive dates within grid', () => {
        const grid = createMonthGrid(2025, 0, 0); // January 2025
        
        // Flatten grid and verify dates are consecutive (1 day apart)
        const allDates = grid.flat();
        for (let i = 1; i < allDates.length; i++) {
            const prevDate = allDates[i - 1];
            const currDate = allDates[i];
            const dayDiff = (currDate.getTime() - prevDate.getTime()) / (1000 * 60 * 60 * 24);
            expect(dayDiff).toBe(1);
        }
    });

    it('adjusts for different first day of week', () => {
        const sundayFirst = createMonthGrid(2025, 0, 0); // Sunday = 0
        const mondayFirst = createMonthGrid(2025, 0, 1); // Monday = 1
        
        // Grids should have different starting dates
        expect(sundayFirst[0][0]).not.toEqual(mondayFirst[0][0]);
        
        // January 2025 starts on Wednesday
        // Sunday-first shows: Sun, Mon, Tue (3 days from prev month)
        // Monday-first shows: Mon, Tue (2 days from prev month)
        // So Monday-first should start later
        expect(mondayFirst[0][0].getTime()).toBeGreaterThan(sundayFirst[0][0].getTime());
    });

    it('handles months starting on different weekdays', () => {
        // January 2025 starts on Wednesday
        const jan2025 = createMonthGrid(2025, 0, 0); // Sunday first
        
        // February 2025 starts on Saturday  
        const feb2025 = createMonthGrid(2025, 1, 0); // Sunday first
        
        // Both should have valid grids
        expect(jan2025.length).toBeGreaterThanOrEqual(4);
        expect(feb2025.length).toBeGreaterThanOrEqual(4);
    });

    it('handles February in leap and non-leap years', () => {
        const feb2024 = createMonthGrid(2024, 1, 0); // Leap year
        const feb2025 = createMonthGrid(2025, 1, 0); // Non-leap year
        
        // Both should be valid grids
        expect(feb2024.length).toBeGreaterThanOrEqual(4);
        expect(feb2025.length).toBeGreaterThanOrEqual(4);
        
        // Verify all dates are consecutive
        const checkConsecutive = (dates: Date[]) => {
            for (let i = 1; i < dates.length; i++) {
                const dayDiff = (dates[i].getTime() - dates[i - 1].getTime()) / (1000 * 60 * 60 * 24);
                expect(dayDiff).toBe(1);
            }
        };
        
        checkConsecutive(feb2024.flat());
        checkConsecutive(feb2025.flat());
    });

    it('creates dates at midnight in local timezone', () => {
        const grid = createMonthGrid(2025, 0, 0);
        const firstDate = grid[0][0];
        
        expect(firstDate.getHours()).toBe(0);
        expect(firstDate.getMinutes()).toBe(0);
        expect(firstDate.getSeconds()).toBe(0);
        expect(firstDate.getMilliseconds()).toBe(0);
    });

    it('includes correct dates for January 2025', () => {
        const grid = createMonthGrid(2025, 0, 0); // January 2025, Sunday first
        const allDates = grid.flat();
        
        // January 1, 2025 is a Wednesday
        // So grid starts on Sunday, December 29, 2024
        expect(allDates[0]).toEqual(new Date(2024, 11, 29));
        
        // Find January 1 (should be 4th cell: Sun, Mon, Tue, Wed)
        expect(allDates[3]).toEqual(new Date(2025, 0, 1));
        
        // Find January 31
        const jan31Index = allDates.findIndex(d => 
            d.getMonth() === 0 && d.getDate() === 31
        );
        expect(allDates[jan31Index]).toEqual(new Date(2025, 0, 31));
    });
});
