import React, {Component} from 'react';
import ReactSlider, {createSliderWithTooltip} from 'rc-slider';
import {assoc, isNil, pick, pipe, omit} from 'ramda';
import computeSliderStyle from '../utils/computeSliderStyle';

import 'rc-slider/assets/index.css';

import {
    sanitizeMarks,
    calcStep,
    setUndefined,
} from '../utils/computeSliderMarkers';
import {propTypes} from '../components/Slider.react';
import {
    formatSliderTooltip,
    transformSliderTooltip,
} from '../utils/formatSliderTooltip';
import LoadingElement from '../utils/LoadingElement';

const MAX_MARKS = 500;

const sliderProps = [
    'min',
    'max',
    'disabled',
    'dots',
    'included',
    'tooltip',
    'vertical',
    'reverse',
    'id',
];

/**
 * A slider component with a single handle.
 */
export default class Slider extends Component {
    constructor(props) {
        super(props);
        this.DashSlider = props.tooltip
            ? createSliderWithTooltip(ReactSlider)
            : ReactSlider;
        this._computeStyle = computeSliderStyle();
        this.state = {value: props.value};
    }

    UNSAFE_componentWillReceiveProps(newProps) {
        if (newProps.tooltip !== this.props.tooltip) {
            this.DashSlider = newProps.tooltip
                ? createSliderWithTooltip(ReactSlider)
                : ReactSlider;
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
            setProps,
            tooltip,
            updatemode,
            min,
            max,
            marks,
            step,
            vertical,
            verticalHeight,
        } = this.props;
        const value = this.state.value;

        // Check if marks exceed 500 limit for performance
        let processedMarks = marks;
        if (marks && typeof marks === 'object' && marks !== null) {
            const marksCount = Object.keys(marks).length;
            if (marksCount > MAX_MARKS) {
                /* eslint-disable no-console */
                console.error(
                    `dcc.Slider: Too many marks (${marksCount}) provided. ` +
                        `For performance reasons, marks are limited to 500. ` +
                        `Using auto-generated marks instead.`
                );
                processedMarks = undefined;
            }
        }

        let tipProps, tipFormatter;
        if (tooltip) {
            /**
             * clone `tooltip` but with renamed key `always_visible` -> `visible`
             * the rc-tooltip API uses `visible`, but `always_visible` is more semantic
             * assigns the new (renamed) key to the old key and deletes the old key
             */
            tipProps = pipe(
                assoc('visible', tooltip.always_visible),
                omit(['always_visible', 'template', 'style', 'transform'])
            )(tooltip);
            if (tooltip.template || tooltip.style || tooltip.transform) {
                tipFormatter = tipValue => {
                    let t = tipValue;
                    if (tooltip.transform) {
                        t = transformSliderTooltip(tooltip.transform, tipValue);
                    }
                    return (
                        <div style={tooltip.style}>
                            {formatSliderTooltip(
                                tooltip.template || '{value}',
                                t
                            )}
                        </div>
                    );
                };
            }
        }

        return (
            <LoadingElement
                id={id}
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
                    value={value}
                    marks={sanitizeMarks({
                        min,
                        max,
                        marks: processedMarks,
                        step,
                    })}
                    max={setUndefined(min, max, processedMarks).max_mark}
                    min={setUndefined(min, max, processedMarks).min_mark}
                    step={
                        step === null && !isNil(processedMarks)
                            ? null
                            : calcStep(min, max, step)
                    }
                    {...pick(sliderProps, this.props)}
                />
            </LoadingElement>
        );
    }
}

Slider.propTypes = propTypes;
