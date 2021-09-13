import {type} from 'ramda';

export const sanitizeOptions = options => {
    if (type(options) === 'Array') {
        if (
            options.length > 0 &&
            ['String', 'Number', 'Bool'].includes(type(options[0]))
        ) {
            return options.map(option => ({
                label: String(option),
                value: option,
            }));
        }
        return options;
    }
    return Object.entries(options).map(([value, label]) => ({
        label,
        value,
    }));
};