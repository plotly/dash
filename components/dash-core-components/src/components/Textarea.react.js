import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {pick} from 'ramda';

const textAreaProps = [
    'id',
    'autoFocus',
    'cols',
    'disabled',
    'form',
    'maxLength',
    'minLength',
    'name',
    'placeholder',
    'readOnly',
    'required',
    'rows',
    'wrap',
    'accessKey',
    'className',
    'contentEditable',
    'contextMenu',
    'dir',
    'draggable',
    'hidden',
    'lang',
    'spellCheck',
    'style',
    'tabIndex',
    'title',
];

/**
 * A basic HTML textarea for entering multiline text.
 *
 */
export default class Textarea extends Component {
    render() {
        const {setProps, loading_state, value} = this.props;

        return (
            <textarea
                data-dash-is-loading={
                    (loading_state && loading_state.is_loading) || undefined
                }
                value={value}
                onChange={e => {
                    setProps({value: e.target.value});
                }}
                onBlur={() => {
                    setProps({
                        n_blur: this.props.n_blur + 1,
                        n_blur_timestamp: Date.now(),
                    });
                }}
                onClick={() => {
                    setProps({
                        n_clicks: this.props.n_clicks + 1,
                        n_clicks_timestamp: Date.now(),
                    });
                }}
                {...pick(textAreaProps, this.props)}
            />
        );
    }
}

Textarea.defaultProps = {
    n_blur: 0,
    n_blur_timestamp: -1,
    n_clicks: 0,
    n_clicks_timestamp: -1,
    persisted_props: ['value'],
    persistence_type: 'local',
};

Textarea.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,

    /**
     * The value of the textarea
     */
    value: PropTypes.string,

    /**
     * The element should be automatically focused after the page loaded.
     */
    autoFocus: PropTypes.string,

    /**
     * Defines the number of columns in a textarea.
     */
    cols: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),

    /**
     * Indicates whether the user can interact with the element.
     */
    disabled: PropTypes.oneOfType([PropTypes.string, PropTypes.bool]),

    /**
     * Indicates the form that is the owner of the element.
     */
    form: PropTypes.string,

    /**
     * Defines the maximum number of characters allowed in the element.
     */
    maxLength: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),

    /**
     * Defines the minimum number of characters allowed in the element.
     */
    minLength: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),

    /**
     * Name of the element. For example used by the server to identify the fields in form submits.
     */
    name: PropTypes.string,

    /**
     * Provides a hint to the user of what can be entered in the field.
     */
    placeholder: PropTypes.string,

    /**
     * Indicates whether the element can be edited.
     * readOnly is an HTML boolean attribute - it is enabled by a boolean or
     * 'readOnly'. Alternative capitalizations `readonly` & `READONLY`
     * are also acccepted.
     */
    readOnly: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.oneOf(['readOnly', 'readonly', 'READONLY']),
    ]),

    /**
     * Indicates whether this element is required to fill out or not.
     * required is an HTML boolean attribute - it is enabled by a boolean or
     * 'required'. Alternative capitalizations `REQUIRED`
     * are also acccepted.
     */
    required: PropTypes.oneOfType([
        PropTypes.oneOf(['required', 'REQUIRED']),
        PropTypes.bool,
    ]),

    /**
     * Defines the number of rows in a text area.
     */
    rows: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),

    /**
     * Indicates whether the text should be wrapped.
     */
    wrap: PropTypes.string,

    /**
     * Defines a keyboard shortcut to activate or add focus to the element.
     */
    accessKey: PropTypes.string,

    /**
     * Often used with CSS to style elements with common properties.
     */
    className: PropTypes.string,

    /**
     * Indicates whether the element's content is editable.
     */
    contentEditable: PropTypes.oneOfType([PropTypes.string, PropTypes.bool]),

    /**
     * Defines the ID of a <menu> element which will serve as the element's context menu.
     */
    contextMenu: PropTypes.string,

    /**
     * Defines the text direction. Allowed values are ltr (Left-To-Right) or rtl (Right-To-Left)
     */
    dir: PropTypes.string,

    /**
     * Defines whether the element can be dragged.
     */
    draggable: PropTypes.oneOfType([
        // enumerated property, not a boolean property: https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/draggable
        PropTypes.oneOf(['true', 'false']),
        PropTypes.bool,
    ]),

    /**
     * Prevents rendering of given element, while keeping child elements, e.g. script elements, active.
     */
    hidden: PropTypes.string,

    /**
     * Defines the language used in the element.
     */
    lang: PropTypes.string,

    /**
     * Indicates whether spell checking is allowed for the element.
     */
    spellCheck: PropTypes.oneOfType([
        // enumerated property, not a boolean property: https://www.w3.org/TR/html51/editing.html#spelling-and-grammar-checking
        PropTypes.oneOf(['true', 'false']),
        PropTypes.bool,
    ]),

    /**
     * Defines CSS styles which will override styles previously set.
     */
    style: PropTypes.object,

    /**
     * Overrides the browser's default tab order and follows the one specified instead.
     */
    tabIndex: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),

    /**
     * Text to be displayed in a tooltip when hovering over the element.
     */
    title: PropTypes.string,

    /**
     * Number of times the textarea lost focus.
     */
    n_blur: PropTypes.number,
    /**
     * Last time the textarea lost focus.
     */
    n_blur_timestamp: PropTypes.number,

    /**
     * Number of times the textarea has been clicked.
     */
    n_clicks: PropTypes.number,
    /**
     * Last time the textarea was clicked.
     */
    n_clicks_timestamp: PropTypes.number,

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
};
