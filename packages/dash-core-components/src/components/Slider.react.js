import React, {Component, PropTypes} from 'react';
import ReactSlider from 'rc-slider';

export default class Slider extends Component {
    render() {
        return (
            <ReactSlider
                onChange={value => {
                    this.props.valueChanged({value});
                }}
                {...this.props}
            />
        );
    }
}

Slider.propTypes = {
    /**
     * Additional CSS class for the root DOM node
     */
    className: PropTypes.string,

    /**
     * If true, the handles can't be moved.
     */
    disabled: PropTypes.bool,

    /**
     * When the step value is greater than 1,
     * you can set the dots to true if you want to
     * render the slider with dots.
     */
    dots: PropTypes.bool,

    /**
     * If the value is true, it means a continuous
     * value is included. Otherwise, it is an independent value.
     */
    included: PropTypes.bool,

    /**
     * Marks on the slider.
     * The key determines the position,
     * and the value determines what will show.
     * If you want to set the style of a specific mark point,
     * the value should be an object which
     * contains style and label properties.
     */
    marks: PropTypes.shape({number: PropTypes.string}),

    /**
     * Minimum allowed value of the slider
     */
    min: PropTypes.number,

    /**
     * Maximum allowed value of the slider
     */
    max: PropTypes.number,

    /**
     * Value by which increments or decrements are made
     */
    step: PropTypes.number,

    /**
     * Key-values pairs describing the labels
     */
    labels: PropTypes.object,

    /**
     * The value of the input
     */
    value: PropTypes.number,

    /**
     * Dash-assigned callback that gets fired when the input changes
     */
    valueChanged: PropTypes.func.isRequired,

    /**
     * If true, the slider will be vertical
     */
    vertical: PropTypes.bool
};
