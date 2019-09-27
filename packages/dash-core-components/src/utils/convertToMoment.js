import moment from 'moment';
import {has} from 'ramda';

export default (newProps, momentProps) => {
    const dest = {};

    momentProps.forEach(key => {
        const value = newProps[key];

        if (value === null || value === undefined) {
            dest[key] = null;

            if (key === 'initial_visible_month') {
                dest[key] = moment();
            }
        } else {
            dest[key] = moment(value);

            if (key === 'max_date_allowed' && has(key, dest)) {
                dest[key].add(1, 'days');
            }
        }
    });

    return dest;
};
