import moment from 'moment';
import {isNil} from 'ramda';

export default {
    extract: propValue => {
        if (!isNil(propValue)) {
            return moment(propValue).startOf('day').format('YYYY-MM-DD');
        }
        return propValue;
    },
    apply: storedValue => storedValue,
};
