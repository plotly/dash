import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {omit} from 'ramda';
import {Range} from 'rc-slider';

/**
 * A double slider with two handles.
 * Used for specifying a range of numerical values.
 */
export default class RangeSlider extends Component {
    constructor(props) {
        super(props);
        this.state = {value: props.value};
    }

    componentWillReceiveProps(newProps) {
        this.setState({value: newProps.value});
    }

    render() {
        const {fireEvent, setProps, updatemode} = this.props;
        const {value} = this.state;
        return (
            <Range
                onChange={value => {
                    this.setState({value});
                    if (updatemode === 'drag') {
                        if (setProps) {setProps({value});}
                        if (fireEvent) {fireEvent('change');}
                    }
                }}
                onAfterChange={value => {
                    if (updatemode === 'mouseup') {
                        if (setProps) {setProps({value});}
                        if (fireEvent) {fireEvent('change');}
                    }
                }}
                value={value}
                {...omit(
                    ['value', 'fireEvent', 'setProps', 'updatemode'],
                     this.props
                 )}
            />
        );
    }
}

RangeSlider.propTypes = {
    id: PropTypes.string,

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
     * The value of the input
     */
    value: PropTypes.arrayOf(PropTypes.number),

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
     * If true, the slider will be vertical
     */
    vertical: PropTypes.bool,

    /**
     * Determines when the component should update
     * its value. If `mouseup`, then the slider
     * will only trigger its value when the user has
     * finished dragging the slider. If `drag`, then
     * the slider will update its value continuously
     * as it is being dragged.
     * Only use `drag` if your updates are fast.
     */
    updatemode: PropTypes.oneOf(['mouseup', 'drag']),

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

RangeSlider.defaultProps = {
    updatemode: 'mouseup'
};
