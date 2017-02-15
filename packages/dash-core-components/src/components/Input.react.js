import React, {Component, PropTypes} from 'react';

export default class Input extends Component {
    render() {

        const {className, id, fireEvent, placeholder,
               style, value, valueChanged} = this.props;

        return (
            <input
                className={className}
                id={id}
                type="text/javascript"
                value={value}
                placeholder={placeholder}
                style={style}
                onChange={e => {
                    if (valueChanged) valueChanged({value: e.target.value});
                    // TODO - Will valueChange finish propagating before
                    // fireEvent takes its state?? might need redux-thunk
                    if (fireEvent) fireEvent({event: 'onChange'});
                }}
                onBlur={e => {
                    if (fireEvent) fireEvent({event: 'onBlur'});
                }}
            />
        );
    }
}

Input.propTypes = {
    /**
     * The class of the input element
     */
    className: PropTypes.string,

    /**
     * The id of the component
     */
    id: PropTypes.string.isRequired,

    /**
     * The input's placeholder
     */
    placeholder: PropTypes.string,

    /**
     * The input's inline styles
     */
    style: PropTypes.object,

    /**
     * The value of the input
     */
    value: PropTypes.string.isRequired,

    /**
     * Dash-assigned callback that gets fired when the input changes.
     */
    fireEvent: PropTypes.func,

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    valueChanged: PropTypes.func

};
