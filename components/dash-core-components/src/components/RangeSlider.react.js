import React, {Component, lazy, Suspense} from 'react';
import PropTypes from 'prop-types';
import rangeSlider from '../utils/LazyLoader/rangeSlider';

const RealRangeSlider = lazy(rangeSlider);

/**
 * A double slider with two handles.
 * Used for specifying a range of numerical values.
 */
export default class RangeSlider extends Component {
    render() {
        return (
            <Suspense fallback={null}>
                <RealRangeSlider {...this.props} />
            </Suspense>
        );
    }
}

RangeSlider.propTypes = {
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
     * Marks on the slider.
     * The key determines the position (a number),
     * and the value determines what will show.
     * If you want to set the style of a specific mark point,
     * the value should be an object which
     * contains style and label properties.
     */
    marks: PropTypes.objectOf(
        PropTypes.oneOfType([
            PropTypes.string,
            PropTypes.exact({
                label: PropTypes.string,
                style: PropTypes.object,
            }),
        ])
    ),

    /**
     * The value of the input
     */
    value: PropTypes.arrayOf(PropTypes.number),

    /**
     * The value of the input during a drag
     */
    drag_value: PropTypes.arrayOf(PropTypes.number),

    /**
     * allowCross could be set as true to allow those handles to cross.
     */
    allowCross: PropTypes.bool,

    /**
     * pushable could be set as true to allow pushing of
     * surrounding handles when moving an handle.
     * When set to a number, the number will be the
     * minimum ensured distance between handles.
     */
    pushable: PropTypes.oneOfType([PropTypes.bool, PropTypes.number]),

    /**
     * If true, the handles can't be moved.
     */
    disabled: PropTypes.bool,

    /**
     * Determine how many ranges to render, and multiple handles
     * will be rendered (number + 1).
     */
    count: PropTypes.number,

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
     * Configuration for tooltips describing the current slider values
     */
    tooltip: PropTypes.exact({
        /**
         * Determines whether tooltips should always be visible
         * (as opposed to the default, visible on hover)
         */
        always_visible: PropTypes.bool,

        /**
         * Determines the placement of tooltips
         * See https://github.com/react-component/tooltip#api
         * top/bottom{*} sets the _origin_ of the tooltip, so e.g. `topLeft`
         * will in reality appear to be on the top right of the handle
         */
        placement: PropTypes.oneOf([
            'left',
            'right',
            'top',
            'bottom',
            'topLeft',
            'topRight',
            'bottomLeft',
            'bottomRight',
        ]),
    }),

    /**
     * Determines when the component should update its `value`
     * property. If `mouseup` (the default) then the slider
     * will only trigger its value when the user has finished
     * dragging the slider. If `drag`, then the slider will
     * update its value continuously as it is being dragged.
     * Note that for the latter case, the `drag_value`
     * property could be used instead.
     */
    updatemode: PropTypes.oneOf(['mouseup', 'drag']),

    /**
     * If true, the slider will be vertical
     */
    vertical: PropTypes.bool,

    /**
     * The height, in px, of the slider if it is vertical.
     */
    verticalHeight: PropTypes.number,

    /**
     * Additional CSS class for the root DOM node
     */
    className: PropTypes.string,

    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,

    /**
     * Dash-assigned callback that gets fired when the value or drag_value changes.
     */
    setProps: PropTypes.func,

    /**
     * Object that holds the loading state object coming from dash-renderer
     */
    loading_state: PropTypes.shape({
        /**
         * Determines if the component is loading or not
         */
        is_loading: PropTypes.bool,
        /**
         * Holds which property is loading
         */
        prop_name: PropTypes.string,
        /**
         * Holds the name of the component that is loading
         */
        component_name: PropTypes.string,
    }),

    /**
     * Used to allow user interactions in this component to be persisted when
     * the component - or the page - is refreshed. If `persisted` is truthy and
     * hasn't changed from its previous value, a `value` that the user has
     * changed while using the app will keep that change, as long as
     * the new `value` also matches what was given originally.
     * Used in conjunction with `persistence_type`.
     */
    persistence: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.string,
        PropTypes.number,
    ]),

    /**
     * Properties whose user interactions will persist after refreshing the
     * component or the page. Since only `value` is allowed this prop can
     * normally be ignored.
     */
    persisted_props: PropTypes.arrayOf(PropTypes.oneOf(['value'])),

    /**
     * Where persisted user changes will be stored:
     * memory: only kept in memory, reset on page refresh.
     * local: window.localStorage, data is kept after the browser quit.
     * session: window.sessionStorage, data is cleared once the browser quit.
     */
    persistence_type: PropTypes.oneOf(['local', 'session', 'memory']),
};

RangeSlider.defaultProps = {
    updatemode: 'mouseup',
    persisted_props: ['value'],
    persistence_type: 'local',
    verticalHeight: 400,
};

export const propTypes = RangeSlider.propTypes;
export const defaultProps = RangeSlider.defaultProps;
