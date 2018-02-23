import PropTypes from 'prop-types';
import React, {Component} from 'react';

/**
 * RadioItems is a component that encapsulates several radio item inputs.
 * The values and labels of the RadioItems is specified in the `options`
 * property and the seleced item is specified with the `value` property.
 * Each radio item is rendered as an input with a surrounding label.
 */

export default class RadioItems extends Component {
    constructor(props) {
        super(props);
        this.state = {value: props.value};
    }

    componentWillReceiveProps(newProps) {
        this.setState({value: newProps.value});
    }

    render() {
        const {
            fireEvent,
            id,
            className,
            style,
            inputClassName,
            inputStyle,
            labelClassName,
            labelStyle,
            options,
            setProps
        } = this.props;
        const {value} = this.state;

        let ids = {};
        if (id) {
            ids = {id, key: id};
        }
        return (
            <div {...ids} className={className} style={style}>
                {options.map(option => (
                    <label style={labelStyle} className={labelClassName} key={option.value}>
                        <input
                            checked={option.value === value}
                            className={inputClassName}
                            disabled={Boolean(option.disabled)}
                            style={inputStyle}
                            type="radio"
                            onChange={() => {
                                this.setState({value: option.value});
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
}

RadioItems.propTypes = {
    id: PropTypes.string,

    /**
     * An array of options
     */
    options: PropTypes.arrayOf(
        PropTypes.shape({
            /**
             * The radio item's label
             */
            label: PropTypes.string,

            /**
             * The value of the radio item. This value
             * corresponds to the items specified in the
             * `values` property.
             */
            value: PropTypes.string,

            /**
             * If true, this radio item is disabled and can't be clicked on.
             */
            disabled: PropTypes.bool
        })
    ),

    /**
     * The currently selected value
     */
    value: PropTypes.string,

    /**
     * The style of the container (div)
     */
    style: PropTypes.object,

    /**
     * The class of the container (div)
     */
    className: PropTypes.string,

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
