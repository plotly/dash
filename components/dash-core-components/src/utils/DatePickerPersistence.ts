import {format, startOfDay, parseISO} from 'date-fns';
import {isNil} from 'ramda';

export default {
    extract: (propValue?: string) => {
        if (isNil(propValue)) {
            return propValue;
        }

        const parsed = parseISO(propValue);
        return format(startOfDay(parsed), 'yyyy-MM-dd');
    },
    apply: (storedValue?: string) => storedValue,
};
