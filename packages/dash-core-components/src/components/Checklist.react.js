import {append, contains, without} from 'ramda';
import React, {PropTypes} from 'react';

/**
 * Checklist is a component that encapsulates several checkboxes.
 * The values and labels of the checklist is specified in the `options`
 * property and the checked items are specified with the `values` property.
 * Each checkbox is rendered as an input with a surrounding label.
 */
export default function Checklist(props) {
    const {
        fireEvent,
        id,
        inputClassName,
        inputStyle,
        labelClassName,
        labelStyle,
        options,
        values,
        setProps
    } = props;
    return (
        <div id={id}>
            {options.map(option => (
                <label
                    key={option.value}
                    style={labelStyle}
                    className={labelClassName}
                >
                    <input
                        checked={contains(option.value, values)}
                        className={inputClassName}
                        disabled={Boolean(option.disabled)}
                        style={inputStyle}
                        type="checkbox"
                        onChange={() => {
                            if (setProps) {
                                let newValues;
                                if (contains(option.value, values)) {
                                    newValues = without([option.value], values);
                                } else {
                                    newValues = append(option.value, values);
                                }
                                setProps({values: newValues});
                            }
                            if (fireEvent) fireEvent({event: 'change'});
                        }}
                    />
                    {option.label}
                </label>
            ))}
        </div>
    );
}

Checklist.propTypes = {
    id: PropTypes.string,
    /**
     * The style of the <input> checkbox element
     */
    inputStyle: PropTypes.object,

    /**
     * The class of the <input> checkbox element
     */
    inputClassName: PropTypes.string,

    /**
     * The style of the <label> that wraps the checkbox input
     *  and the option's label
     */
    labelStyle: PropTypes.object,

    /**
     * The class of the <label> that wraps the checkbox input
     *  and the option's label
     */
    labelClassName: PropTypes.string,

    /**
     * An array of options
     */
    options: PropTypes.shape({
        /**
         * The checkbox's label
         */
        label: PropTypes.string,

        /**
         * The value of the checkbox. This value
         * corresponds to the items specified in the
         * `values` property.
         */
        value: PropTypes.string,

        /**
         * If true, this checkbox is disabled and can't be clicked on.
         */
        disabled: PropTypes.bool
    }),

    /**
     * The currently selected value
     */
    values: PropTypes.arrayOf(PropTypes.string),

    /**
     * Dash-assigned callback that gets fired when the checkbox item gets selected.
     */
    fireEvent: PropTypes.func,

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    setProps: PropTypes.func,

    dashEvents: PropTypes.oneOf(['change'])
};

Checklist.defaultProps = {
    inputStyle: {},
    inputClassName: '',
    labelStyle: {},
    labelClassName: '',
    options: []
};
