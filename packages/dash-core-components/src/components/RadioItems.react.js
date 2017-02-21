import React, {PropTypes} from 'react';

export default function Radio(props) {
    const {
        fireEvent,
        inputClassName,
        inputStyle,
        labelClassName,
        labelStyle,
        options,
        value,
        valueChanged
    } = props;
    return (
        <div>
            {options.map(option => (
                <label style={labelStyle} className={labelClassName}>
                    <input
                        checked={option.value === value}
                        className={inputClassName}
                        disabled={Boolean(option.disabled)}
                        style={inputStyle}
                        type="radio"
                        onChange={() => {
                            if (valueChanged) valueChanged({value: option.value});
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
    value: PropTypes.string,

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
