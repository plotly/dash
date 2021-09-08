import PropTypes from "prop-types";

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
)

/**
 * Array of options as string[]
 */
const optionArrayShorthandType = PropTypes.arrayOf(PropTypes.string)

/**
 * Object of options as {label: value}[]
 */
const optionObjectShorthandType = PropTypes.objectOf(PropTypes.string)

export const optionsType = PropTypes.oneOfType([defaultOptionType, optionArrayShorthandType, optionObjectShorthandType])
