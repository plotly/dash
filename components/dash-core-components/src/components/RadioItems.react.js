import PropTypes from 'prop-types';
import React, {Component} from 'react';
import './css/react-select@1.0.0-rc.3.min.css';
import {sanitizeOptions} from '../utils/optionTypes';
import LoadingElement from '../utils/LoadingElement';

/**
 * RadioItems is a component that encapsulates several radio item inputs.
 * The values and labels of the RadioItems is specified in the `options`
 * property and the seleced item is specified with the `value` property.
 * Each radio item is rendered as an input with a surrounding label.
 */

export default class RadioItems extends Component {
    render() {
        const {
            id,
            className,
            style,
            inputClassName,
            inputStyle,
            labelClassName,
            labelStyle,
            options,
            setProps,
            value,
            inline,
        } = this.props;

        let ids = {};
        if (id) {
            ids = {id, key: id};
        }
        return (
            <LoadingElement {...ids} className={className} style={style}>
                {sanitizeOptions(options).map(option => (
                    <label
                        style={{
                            display: inline ? 'inline-block' : 'block',
                            ...labelStyle,
                        }}
                        className={labelClassName}
                        key={option.value}
                        title={option.title}
                    >
                        <input
                            checked={option.value === value}
                            className={inputClassName}
                            disabled={Boolean(option.disabled)}
                            style={inputStyle}
                            type="radio"
                            onChange={() => {
                                setProps({value: option.value});
                            }}
                        />
                        {option.label}
                    </label>
                ))}
            </LoadingElement>
        );
    }
}

RadioItems.propTypes = {
    /**
     * An array of options, or inline dictionary of options
     */
    options: PropTypes.oneOfType([
        /**
         * Array of options where the label and the value are the same thing - [string|number|bool]
         */
        PropTypes.arrayOf(
            PropTypes.oneOfType([
                PropTypes.string,
                PropTypes.number,
                PropTypes.bool,
            ])
        ),
        /**
         * Simpler `options` representation in dictionary format. The order is not guaranteed.
         * {`value1`: `label1`, `value2`: `label2`, ... }
         * which is equal to
         * [{label: `label1`, value: `value1`}, {label: `label2`, value: `value2`}, ...]
         */
        PropTypes.object,
        /**
         * An array of options {label: [string|number], value: [string|number]},
         * an optional disabled field can be used for each option
         */
        PropTypes.arrayOf(
            PropTypes.exact({
                /**
                 * The option's label
                 */
                label: PropTypes.node.isRequired,

                /**
                 * The value of the option. This value
                 * corresponds to the items specified in the
                 * `value` property.
                 */
                value: PropTypes.oneOfType([
                    PropTypes.string,
                    PropTypes.number,
                    PropTypes.bool,
                ]).isRequired,

                /**
                 * If true, this option is disabled and cannot be selected.
                 */
                disabled: PropTypes.bool,

                /**
                 * The HTML 'title' attribute for the option. Allows for
                 * information on hover. For more information on this attribute,
                 * see https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/title
                 */
                title: PropTypes.string,
            })
        ),
    ]),

    /**
     * The currently selected value
     */
    value: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
        PropTypes.bool,
    ]),

    /**
     * Indicates whether the options labels should be displayed inline (true=horizontal)
     * or in a block (false=vertical).
     */
    inline: PropTypes.bool,

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
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    setProps: PropTypes.func,

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

RadioItems.defaultProps = {
    inputStyle: {},
    inputClassName: '',
    labelStyle: {},
    labelClassName: '',
    options: [],
    persisted_props: ['value'],
    persistence_type: 'local',
    inline: false,
};
