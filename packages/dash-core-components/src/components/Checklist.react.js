import {append, contains, without} from 'ramda';
import React, {PropTypes} from 'react';


export default function Radio(props) {
    const {
        fireEvent,
        inputClassName,
        inputStyle,
        labelClassName,
        labelStyle,
        options,
        values,
        valueChanged
    } = props;
    return (
        <div>
            {options.map(option => (
                <label style={labelStyle} className={labelClassName}>
                    <input
                        checked={contains(option.value, values)}
                        className={inputClassName}
                        disabled={Boolean(option.disabled)}
                        style={inputStyle}
                        type="checkbox"
                        onChange={() => {
                            if (valueChanged) {
                                let newValues;
                                if (contains(option.value, values)) {
                                    newValues = without([option.value], values);
                                } else {
                                    newValues = append(option.value, values);
                                }
                                valueChanged({values: newValues});
                            }
                            if (fireEvent) fireEvent({event: 'onChange'});
                        }}
                    />
                    {option.label}
                </label>
            ))}
        </div>
    );
}

Radio.propTypes = {
    /**
     * The style of the <input> radio element
     */
    inputStyle: PropTypes.object,

    /**
     * The class of the <input> radio element
     */
    inputClassName: PropTypes.string,

    /**
     * The style of the <label> that wraps the radio input
     *  and the option's label
     */
    labelStyle: PropTypes.object,

    /**
     * The class of the <label> that wraps the radio input
     *  and the option's label
     */
    labelClassName: PropTypes.string,

    /**
     * An array of options
     */
    options: PropTypes.shape({
        label: PropTypes.string,
        value: PropTypes.string,
        disabled: PropTypes.bool
    }),

    /**
     * The currently selected value
     */
    values: PropTypes.arrayOf(PropTypes.string),

    /**
     * Dash-assigned callback that gets fired when the radio item gets selected.
     */
    fireEvent: PropTypes.func,

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    valueChanged: PropTypes.func
};

Radio.defaultProps = {
    inputStyle: {},
    inputClassName: '',
    labelStyle: {},
    labelClassName: '',
    options: []
};
