import moment from 'moment';
import {has} from 'ramda';

export default (newProps, momentProps) => {
    const dest = {};

    momentProps.forEach(key => {
        const value = newProps[key];

        if (value === null || value === undefined) {
            dest[key] = null;

            if (key === 'initial_visible_month') {
                dest[key] = moment(
                    newProps.start_date ||
                        newProps.min_date_allowed ||
                        newProps.end_date ||
                        newProps.max_date_allowed ||
                        undefined
                );
            }
        } else if (Array.isArray(value)) {
            dest[key] = value.map(d => moment(d));
        } else {
            dest[key] = moment(value);

            if (key === 'max_date_allowed' && has(key, dest)) {
                dest[key].add(1, 'days');
            }
        }
    });

    return dest;
};
