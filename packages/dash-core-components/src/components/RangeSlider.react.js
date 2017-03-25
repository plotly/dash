import React, {Component, PropTypes} from 'react';
import {Range} from 'rc-slider';

/**
 * A double slider with two handles.
 * Used for specifying a range of numerical values.
 */
export default class RangeSlider extends Component {
    render() {
        const {setProps, fireEvent} = this.props;
        return (
            <Range
                onChange={value => {
                    if (setProps) setProps({value});
                    if (fireEvent) fireEvent('change');
                }}
                {...this.props}
            />
        );
    }
}

RangeSlider.propTypes = {
    id: PropTypes.string,
    /**
     * allowCross could be set as true to allow those handles to cross.
     */
    allowCross: PropTypes.bool,

    /**
     * Additional CSS class for the root DOM node
     */
    className: PropTypes.string,

    /**
     * Determine how many ranges to render, and multiple handles
     * will be rendered (number + 1).
     */
    count: PropTypes.number,

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
    marks: PropTypes.shape({
        number: PropTypes.oneOfType([
            /**
             * The label of the mark
             */
            PropTypes.string,

            /**
             * The style and label of the mark
             */
            PropTypes.shape({
                style: PropTypes.object,
                label: PropTypes.string
            })
        ])
    }),

    /**
     * Minimum allowed value of the slider
     */
    min: PropTypes.number,

    /**
     * Maximum allowed value of the slider
     */
    max: PropTypes.number,

    /**
     * pushable could be set as true to allow pushing of
     * surrounding handles when moving an handle.
     * When set to a number, the number will be the
     * minimum ensured distance between handles.
     */
    pushable: PropTypes.oneOfType([PropTypes.bool, PropTypes.number]),

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
    value: PropTypes.arrayOf(PropTypes.number),

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
