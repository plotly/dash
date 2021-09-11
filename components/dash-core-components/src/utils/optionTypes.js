import PropTypes from 'prop-types';
import {type} from 'ramda';

/**
 * An array of options {label: [string|number], value: [string|number]},
 * an optional disabled field can be used for each option
 */
const defaultOptionType = PropTypes.arrayOf(
    PropTypes.exact({
        /**
         * The option's label
         */
        label: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
            .isRequired,

        /**
         * The value of the option. This value
         * corresponds to the items specified in the
         * `value` property.
         */
        value: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
            .isRequired,

        /**
         * If true, this option is disabled and cannot be selected.
         */
        disabled: PropTypes.bool,

        /**
         * The HTML 'title' attribute for the option. Allows for
         * information on hover. For more information on this attribute,
         * see https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/title
         */
        title: PropTypes.string,
    })
);

/**
 * Array of options as string[]
 */
const optionArrayShorthandType = PropTypes.arrayOf(
    PropTypes.oneOfType([PropTypes.string, PropTypes.number, PropTypes.bool])
);

/**
 * Simpler `options` representation in dictionary format
 * {`value1`: `label1`, `value2`: `label2`, ... }
 * which is equal to
 * [{label: `label1`, value: `value1`}, {label: `label2`, value: `value2`}, ...]
 */
const optionObjectShorthandType = PropTypes.objectOf(
    PropTypes.oneOfType([PropTypes.string, PropTypes.number, PropTypes.bool])
);

export const optionsType = PropTypes.oneOfType([
    defaultOptionType,
    optionArrayShorthandType,
    optionObjectShorthandType,
]);

export const sanitizeOptions = options => {
    if (type(options) === 'Array') {
        if (options.length > 0 && type(options[0]) === 'String') {
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
