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
    'id',
] as const;

interface SliderProps {
    /**
     * Minimum allowed value of the slider
     */
    min: number;

    /**
     * Maximum allowed value of the slider
     */
    max: number;

    /**
     * Value by which increments or decrements are made
     */
    step?: number | null;

    /**
     * Marks on the slider.
     * The key determines the position (a number),
     * and the value determines what will show.
     * If you want to set the style of a specific mark point,
     * the value should be an object which
     * contains style and label properties.
     */
    marks?: {
        [key: number]: string | {label: string; style?: React.CSSProperties};
    };

    /**
     * The value of the input
     */
    value?: number | null;

    /**
     * The value of the input during a drag
     */
    drag_value?: number;

    /**
     * If true, the handles can't be moved.
     */
    disabled?: boolean;

    /**
     * When the step value is greater than 1,
     * you can set the dots to true if you want to
     * render the slider with dots.
     */
    dots?: boolean;

    /**
     * If the value is true, it means a continuous
     * value is included. Otherwise, it is an independent value.
     */
    included?: boolean;

    /**
     * Configuration for tooltips describing the current slider value
     */
    tooltip?: {
        /**
         * Determines whether tooltips should always be visible
         * (as opposed to the default, visible on hover)
         */
        always_visible?: boolean;

        /**
         * Determines the placement of tooltips
         * See https://github.com/react-component/tooltip#api
         * top/bottom{*} sets the _origin_ of the tooltip, so e.g. `topLeft`
         * will in reality appear to be on the top right of the handle
         */
        placement?:
            | 'left'
            | 'right'
            | 'top'
            | 'bottom'
            | 'topLeft'
            | 'topRight'
            | 'bottomLeft'
            | 'bottomRight';

        /**
         * Template string to display the tooltip in.
         * Must contain `{value}`, which will be replaced with either
         * the default string representation of the value or the result of the
         * transform function if there is one.
         */
        template?: string;

        /**
         * Custom style for the tooltip.
         */
        style?: React.CSSProperties;

        /**
         * Reference to a function in the `window.dccFunctions` namespace.
         * This can be added in a script in the asset folder.
         *
         * For example, in `assets/tooltip.js`:
         * ```
         * window.dccFunctions = window.dccFunctions || {};
         * window.dccFunctions.multByTen = function(value) {
         *     return value * 10;
         * }
         * ```
         * Then in the component `tooltip={'transform': 'multByTen'}`
         */
        transform?: string;
    };

    /**
     * Determines when the component should update its `value`
     * property. If `mouseup` (the default) then the slider
     * will only trigger its value when the user has finished
     * dragging the slider. If `drag`, then the slider will
     * update its value continuously as it is being dragged.
     * If you want different actions during and after drag,
     * leave `updatemode` as `mouseup` and use `drag_value`
     * for the continuously updating value.
     */
    updatemode?: 'mouseup' | 'drag';

    /**
     * If true, the slider will be vertical
     */
    vertical?: boolean;

    /**
     * The height, in px, of the slider if it is vertical.
     */
    verticalHeight?: number;

    /**
     * Additional CSS class for the root DOM node
     */
    className?: string;

    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id?: string;

    /**
     * Dash-assigned callback that gets fired when the value or drag_value changes.
     */
    setProps: (props: Partial<SliderProps>) => void;

    /**
     * Used to allow user interactions in this component to be persisted when
     * the component - or the page - is refreshed. If `persisted` is truthy and
     * hasn't changed from its previous value, a `value` that the user has
     * changed while using the app will keep that change, as long as
     * the new `value` also matches what was given originally.
     * Used in conjunction with `persistence_type`.
     */
    persistence?: boolean | string | number;

    /**
     * Properties whose user interactions will persist after refreshing the
     * component or the page. Since only `value` is allowed this prop can
     * normally be ignored.
     */
    persisted_props?: ['value'];

    /**
     * Where persisted user changes will be stored:
     * memory: only kept in memory, reset on page refresh.
     * local: window.localStorage, data is kept after the browser quit.
     * session: window.sessionStorage, data is cleared once the browser quit.
     */
    persistence_type?: 'local' | 'session' | 'memory';
}

interface SliderState {
    value: number | null;
}

/**
 * A slider component with a single handle.
 */
export default class Slider extends Component<SliderProps, SliderState> {
    private DashSlider: any;
    private _computeStyle: any;

    constructor(props: SliderProps) {
        super(props);
        this.DashSlider = props.tooltip
            ? createSliderWithTooltip(ReactSlider)
            : ReactSlider;
        this._computeStyle = computeSliderStyle();
        this.state = {value: props.value || null};
    }

    UNSAFE_componentWillReceiveProps(newProps: SliderProps) {
        if (newProps.tooltip !== this.props.tooltip) {
            this.DashSlider = newProps.tooltip
                ? createSliderWithTooltip(ReactSlider)
                : ReactSlider;
        }
        if (newProps.value !== this.props.value) {
            this.props.setProps({drag_value: newProps.value || undefined});
            this.setState({value: newProps.value || null});
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

        let tipProps: any,
            tipFormatter: ((value: number) => JSX.Element) | undefined;
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
                tipFormatter = (tipValue: number) => {
                    let t: number | string = tipValue;
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
                    onChange={(value: number) => {
                        if (updatemode === 'drag') {
                            setProps({value: value, drag_value: value});
                        } else {
                            this.setState({value: value});
                            setProps({drag_value: value});
                        }
                    }}
                    onAfterChange={(value: number) => {
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
                        getTooltipContainer: (node: any) => node,
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

// PropTypes removed - handled by TypeScript in the new Slider component
