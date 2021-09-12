import PropTypes from 'prop-types';
import {append, includes, without} from 'ramda';
import React, {Component} from 'react';
import {optionsType, sanitizeOptions} from '../utils/optionTypes';

/**
 * Checklist is a component that encapsulates several checkboxes.
 * The values and labels of the checklist are specified in the `options`
 * property and the checked items are specified with the `value` property.
 * Each checkbox is rendered as an input with a surrounding label.
 */
export default class Checklist extends Component {
    render() {
        const {
            className,
            id,
            inputClassName,
            inputStyle,
            labelClassName,
            labelStyle,
            options,
            setProps,
            style,
            loading_state,
            value,
            inline,
        } = this.props;
        return (
            <div
                data-dash-is-loading={
                    (loading_state && loading_state.is_loading) || undefined
                }
                id={id}
                style={style}
                className={className}
            >
                {sanitizeOptions(options).map(option => {
                    return (
                        <label
                            key={option.value}
                            style={Object.assign(
                                {},
                                labelStyle,
                                inline ? {display: 'inline'} : {}
                            )}
                            className={labelClassName}
                        >
                            <input
                                checked={includes(option.value, value)}
                                className={inputClassName}
                                disabled={Boolean(option.disabled)}
                                style={inputStyle}
                                type="checkbox"
                                onChange={() => {
                                    let newValue;
                                    if (includes(option.value, value)) {
                                        newValue = without(
                                            [option.value],
                                            value
                                        );
                                    } else {
                                        newValue = append(option.value, value);
                                    }
                                    setProps({value: newValue});
                                }}
                            />
                            {option.label}
                        </label>
                    );
                })}
            </div>
        );
    }
}

Checklist.propTypes = {
    /**
     * An array of options
     */
    options: optionsType,

    /**
     * The currently selected value
     */
    value: PropTypes.arrayOf(
        PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    ),

    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,

    /**
     * The class of the container (div)
     */
    className: PropTypes.string,

    /**
     * The style of the container (div)
     */
    style: PropTypes.object,

    /**
     * The style of the <input> checkbox element
     */
    inputStyle: PropTypes.object,

    /**
     * The class of the <input> checkbox element
     */
    inputClassName: PropTypes.string,

    /**
     * The style of the <label> that wraps the checkbox input
     *  and the option's label
     */
    labelStyle: PropTypes.object,

    /**
     * The class of the <label> that wraps the checkbox input
     *  and the option's label
     */
    labelClassName: PropTypes.string,

    /**
     * Dash-assigned callback that gets fired when the value changes.
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

    /**
     * Indicates whether labelStyle should be inline or not
     * True: Automatically set { 'display': 'inline' } to labelStyle
     * False: No additional behavior to expect
     */
    inline: PropTypes.bool,
};

Checklist.defaultProps = {
    inputStyle: {},
    inputClassName: '',
    labelStyle: {},
    labelClassName: '',
    options: [],
    value: [],
    persisted_props: ['value'],
    persistence_type: 'local',
    inline: false,
};
