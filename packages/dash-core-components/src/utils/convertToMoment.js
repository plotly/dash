import moment from 'moment';
import R from 'ramda';

export default (newProps, momentProps) => {
    const dest = {};

    momentProps.forEach(key => {
        const value = newProps[key];

        switch (R.type(value)) {
            case 'Undefined':
                return;
            case 'Null':
                dest[key] = null;
                return;
            default:
                dest[key] = moment(value);
        }

        if (key === 'max_date_allowed' && R.has(key, dest)) {
            dest[key].add(1, 'days');
        }
    });

    return dest;
};
