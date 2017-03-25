import React, {Component, PropTypes} from 'react';

/**
 * A basic HTML input control for entering text, numbers, or passwords.
 *
 * Note that checkbox and radio types are supported through
 * the Checklist and RadioItems component. Dates, times, and file uploads
 * are also supported through separate components.
 */
export default class Input extends Component {
    render() {

        const {
            className,
            id,
            fireEvent,
            placeholder,
            style,
            value,
            type,
            setProps
        } = this.props;

        return (
            <input
                className={className}
                id={id}
                type={type}
                value={value}
                placeholder={placeholder}
                style={style}
                onChange={e => {
                    if (setProps) setProps({value: e.target.value});
                    if (fireEvent) fireEvent({event: 'change'});
                }}
                onBlur={() => {
                    if (fireEvent) fireEvent({event: 'blur'});
                }}
            />
        );
    }
}

Input.propTypes = {
    id: PropTypes.string,
    /**
     * The value of the input
     */
    value: PropTypes.string,

    /**
     * A hint to the user of what can be entered in the control.
     * Note: Do not use the placeholder attribute instead of a Label element,
     * their purposes are different.
     * The Label attribute describes the role of the form element
     * (i.e. it indicates what kind of information is expected),
     * and the placeholder attribute is a hint about the format
     * that the content should take.
     * There are cases in which the placeholder attribute is
     * never displayed to the user, so the form must be understandable
     * without it.
     */
    placeholder: PropTypes.string,

    /**
     * The input's inline styles
     */
    style: PropTypes.object,

    /**
     * The class of the input element
     */
    className: PropTypes.string,

    /**
     * The type of control to render.
     */
    type: PropTypes.oneOf([
        'text', 'number', 'password'
    ]),

    /**
     * If disabled, then the input can not be edited
     */
    disabled: PropTypes.bool,

    /**
     * Dash-assigned callback that gets fired when the input changes.
     */
    fireEvent: PropTypes.func,

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    setProps: PropTypes.func,

    dashEvents: PropTypes.oneOf(['blur', 'change'])
};
