import React, {PropTypes} from 'react';

/**
 * RadioItems is a component that encapsulates several radio item inputs.
 * The values and labels of the RadioItems is specified in the `options`
 * property and the seleced item is specified with the `value` property.
 * Each radio item is rendered as an input with a surrounding label.
 */

export default function RadioItems(props) {
    const {
        fireEvent,
        id,
        inputClassName,
        inputStyle,
        labelClassName,
        labelStyle,
        options,
        value,
        setProps
    } = props;
    let ids = {};
    if (id) {
        ids = {id, key: id};
    }
    return (
        <div {...ids}>
            {options.map(option => (
                <label style={labelStyle} className={labelClassName}>
                    <input
                        checked={option.value === value}
                        className={inputClassName}
                        disabled={Boolean(option.disabled)}
                        style={inputStyle}
                        type="radio"
                        onChange={() => {
                            if (setProps) setProps({value: option.value});
                            if (fireEvent) fireEvent({event: 'change'});
                        }}
                    />
                    {option.label}
                </label>
            ))}
        </div>
    );
}

RadioItems.propTypes = {
    id: PropTypes.string,
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
    setProps: PropTypes.func,

    dashEvents: PropTypes.oneOf(['change'])
};

RadioItems.defaultProps = {
    inputStyle: {},
    inputClassName: '',
    labelStyle: {},
    labelClassName: '',
    options: []
};
