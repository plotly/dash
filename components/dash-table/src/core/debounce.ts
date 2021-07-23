import {ResultFn} from 'core/generic';
import Logger from 'core/Logger';

export default function <TArgs extends any[]>(
    fn: ResultFn<TArgs, any>,
    wait: number
) {
    let lastTimestamp = 0;
    let handle: any;

    return (...args: TArgs) => {
        const now = Date.now();
        const delay = Math.min(now - lastTimestamp, wait);

        if (handle) {
            Logger.debug('debounce -- clearTimeout');
            clearTimeout(handle);
        }

        handle = setTimeout(() => {
            Logger.debug('debounce -- execute!');
            fn(...args);
            lastTimestamp = Date.now();
        }, delay);
    };
}
