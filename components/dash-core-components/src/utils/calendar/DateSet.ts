import {dateAsNum, numAsDate, strAsDate} from './helpers';

/**
 * A Set-like collection for Date objects that provides O(1) lookup performance.
 * Internally uses date keys (days since Unix epoch) for efficient storage and comparison.
 */
export class DateSet {
    private keys: Set<number>;

    constructor(dates?: (string | Date | undefined)[] | DateSet) {
        if (dates instanceof DateSet) {
            // Copy constructor
            this.keys = new Set(dates.keys);
        } else if (dates) {
            const parsedDates = dates
                .map(d => (typeof d === 'string' ? strAsDate(d) : d))
                .filter((d): d is Date => d !== undefined)
                .map(dateAsNum);
            this.keys = new Set(parsedDates);
        } else {
            this.keys = new Set();
        }
    }

    has(date: Date): boolean {
        return this.keys.has(dateAsNum(date));
    }

    add(date: Date): this {
        this.keys.add(dateAsNum(date));
        return this;
    }

    delete(date: Date): boolean {
        return this.keys.delete(dateAsNum(date));
    }

    clear(): void {
        this.keys.clear();
    }

    get size(): number {
        return this.keys.size;
    }

    /**
     * Iterate over dates in the set (in chronological order).
     */
    *[Symbol.iterator](): Iterator<Date> {
        // Sort keys to provide chronological iteration
        const sortedKeys = Array.from(this.keys).sort((a, b) => a - b);
        for (const key of sortedKeys) {
            yield numAsDate(key);
        }
    }

    /**
     * Create a DateSet from a date range.
     * @param start - Start date (inclusive)
     * @param end - End date (inclusive)
     * @param excluded - Optional array of dates to exclude from the range
     */
    static fromRange(start?: Date, end?: Date, excluded?: Date[]): DateSet {
        if (!start && !end) {
            return new DateSet();
        }

        if (!start || !end) {
            const singleDate = start ?? end;
            return singleDate ? new DateSet([singleDate]) : new DateSet();
        }

        const k1 = dateAsNum(start);
        const k2 = dateAsNum(end);
        const [startKey, endKey] = [k1, k2].sort((a, b) => a - b);

        const dateSet = new DateSet();
        for (let key = startKey; key <= endKey; key++) {
            dateSet.keys.add(key);
        }

        excluded?.forEach(date => dateSet.delete(date));
        return dateSet;
    }

    /**
     * Get the earliest date in the set.
     */
    min(): Date | undefined {
        if (this.keys.size === 0) {
            return undefined;
        }
        const minKey = Math.min(...this.keys);
        return numAsDate(minKey);
    }

    /**
     * Get the latest date in the set.
     */
    max(): Date | undefined {
        if (this.keys.size === 0) {
            return undefined;
        }
        const maxKey = Math.max(...this.keys);
        return numAsDate(maxKey);
    }
}
