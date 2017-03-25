import React, {Component, PropTypes} from 'react';
import ReactSlider from 'rc-slider';

/**
 * A numerical slider with a single handle.
 */
export default class Slider extends Component {
    render() {
        const {setProps, fireEvent} = this.props;
        return (
            <ReactSlider
                onChange={value => {
                    if (setProps) setProps({value});
                    if (fireEvent) fireEvent('change');
                }}
                {...this.props}
            />
        );
    }
}

Slider.propTypes = {
    id: PropTypes.string,
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
     * If true, the slider will be vertical
     */
    vertical: PropTypes.bool,

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
