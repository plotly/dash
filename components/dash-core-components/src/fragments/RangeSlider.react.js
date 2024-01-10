import React, {Component} from 'react';
import {assoc, pick, isNil, pipe, dissoc} from 'ramda';
import {Range, createSliderWithTooltip} from 'rc-slider';
import computeSliderStyle from '../utils/computeSliderStyle';

import 'rc-slider/assets/index.css';
import {
    calcValue,
    sanitizeMarks,
    calcStep,
    setUndefined,
} from '../utils/computeSliderMarkers';
import {propTypes, defaultProps} from '../components/RangeSlider.react';
import {formatSliderTooltip} from '../utils/formatSliderTooltip';

const sliderProps = [
    'min',
    'max',
    'allowCross',
    'pushable',
    'disabled',
    'count',
    'dots',
    'included',
    'tooltip',
    'vertical',
    'id',
];

export default class RangeSlider extends Component {
    constructor(props) {
        super(props);
        this.DashSlider = props.tooltip
            ? createSliderWithTooltip(Range)
            : Range;
        this._computeStyle = computeSliderStyle();
        this.state = {value: props.value};
    }

    UNSAFE_componentWillReceiveProps(newProps) {
        if (newProps.tooltip !== this.props.tooltip) {
            this.DashSlider = newProps.tooltip
                ? createSliderWithTooltip(Range)
                : Range;
        }
        if (newProps.value !== this.props.value) {
            this.props.setProps({drag_value: newProps.value});
            this.setState({value: newProps.value});
        }
    }

    UNSAFE_componentWillMount() {
        if (this.props.value !== null) {
            this.props.setProps({drag_value: this.props.value});
            this.setState({value: this.props.value});
        }
    }

    render() {
        const {
            className,
            id,
            loading_state,
            setProps,
            tooltip,
            updatemode,
            vertical,
            verticalHeight,
            min,
            max,
            marks,
            step,
        } = this.props;
        const value = this.state.value;

        let tipProps, tipFormatter;
        if (tooltip) {
            /**
             * clone `tooltip` but with renamed key `always_visible` -> `visible`
             * the rc-tooltip API uses `visible`, but `always_visible` is more semantic
             * assigns the new (renamed) key to the old key and deletes the old key
             */
            tipProps = pipe(
                assoc('visible', tooltip.always_visible),
                dissoc('always_visible'),
                dissoc('format'),
                dissoc('style')
            )(tooltip);
            if (tooltip.format || tooltip.style) {
                tipFormatter = tipValue => (
                    <div style={tooltip.style}>
                        {formatSliderTooltip(
                            tooltip.format || '{value}',
                            tipValue
                        )}
                    </div>
                );
            }
        }

        return (
            <div
                id={id}
                data-dash-is-loading={
                    (loading_state && loading_state.is_loading) || undefined
                }
                className={className}
                style={this._computeStyle(vertical, verticalHeight, tooltip)}
            >
                <this.DashSlider
                    onChange={value => {
                        if (updatemode === 'drag') {
                            setProps({value: value, drag_value: value});
                        } else {
                            this.setState({value: value});
                            setProps({drag_value: value});
                        }
                    }}
                    onAfterChange={value => {
                        if (updatemode === 'mouseup') {
                            setProps({value});
                        }
                    }}
                    /*
                    if/when rc-slider or rc-tooltip are updated to latest versions,
                    we will need to revisit this code as the getTooltipContainer function will need to be a prop instead of a nested property
                    */
                    tipProps={{
                        ...tipProps,
                        getTooltipContainer: node => node,
                    }}
                    tipFormatter={tipFormatter}
                    style={{position: 'relative'}}
                    value={value ? value : calcValue(min, max, value)}
                    marks={sanitizeMarks({min, max, marks, step})}
                    max={setUndefined(min, max, marks).max_mark}
                    min={setUndefined(min, max, marks).min_mark}
                    step={
                        step === null && !isNil(marks)
                            ? null
                            : calcStep(min, max, step)
                    }
                    {...pick(sliderProps, this.props)}
                />
            </div>
        );
    }
}

RangeSlider.propTypes = propTypes;
RangeSlider.defaultProps = defaultProps;
