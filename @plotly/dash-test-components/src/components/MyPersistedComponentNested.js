import React, {PureComponent} from 'react';
import PropTypes from 'prop-types';

// simple function to substitute is-numeric for our use case
const isNumber = (n) => {
    return !isNaN(parseFloat(n)) && isFinite(n);
}

// eslint-disable-next-line no-implicit-coercion
const convert = val => (isNumber(val) ? +val : NaN);

const isEquivalent = (v1, v2) => v1 === v2 || (isNaN(v1) && isNaN(v2));

// using these inline functions instead of ramda
const isNil = val => val == null

const omit = (key, obj) => {
    const { [key]: omitted, ...rest } = obj;
    return rest;
  }

/**
 * Adapted dcc input component for persistence tests.
 *
 * Note that some unnecessary props have been removed.
 */
export default class MyPersistedComponentNested extends PureComponent {
    constructor(props) {
        super(props);

        this.input = React.createRef();

        this.onChange = this.onChange.bind(this);
        this.onEvent = this.onEvent.bind(this);
        this.onKeyPress = this.onKeyPress.bind(this);
        this.setInputValue = this.setInputValue.bind(this);
        this.setPropValue = this.setPropValue.bind(this);
    }

    UNSAFE_componentWillReceiveProps(nextProps) {
        const {value} = this.input.current;
        const valueAsNumber = convert(value);
        this.setInputValue(
            isNil(valueAsNumber) ? value : valueAsNumber,
            nextProps.value
        );
        if (this.props.type !== 'number') {
            this.setState({value: nextProps.value});
        }
    }

    componentDidMount() {
        const {value} = this.input.current;
        const valueAsNumber = convert(value);
        this.setInputValue(
            isNil(valueAsNumber) ? value : valueAsNumber,
            this.props.value
        );
    }

    UNSAFE_componentWillMount() {
        if (this.props.type !== 'number') {
            this.setState({value: this.props.value});
        }
    }

    render() {
        const valprops =
            this.props.type === 'number' ? {} : {value: this.state.value};
        const {loading_state} = this.props;
        return (
            <input
                data-dash-is-loading={
                    (loading_state && loading_state.is_loading) || undefined
                }
                ref={this.input}
                onChange={this.onChange}
                onKeyPress={this.onKeyPress}
                {...valprops}
                {...omit(
                    [
                        'debounce',
                        'value',
                        'n_submit',
                        'n_submit_timestamp',
                        'selectionDirection',
                        'selectionEnd',
                        'selectionStart',
                        'setProps',
                        'loading_state',
                    ],
                    this.props
                )}
            />
        );
    }

    setInputValue(base, value) {
        const __value = value;
        base = this.input.current.checkValidity() ? convert(base) : NaN;
        value = convert(value);

        if (!isEquivalent(base, value)) {
            this.input.current.value = isNumber(value) ? value : __value;
        }
    }

    setPropValue(base, value) {
        base = convert(base);
        value = this.input.current.checkValidity() ? convert(value) : NaN;

        if (!isEquivalent(base, value)) {
            this.props.setProps({value});
        }
    }

    onEvent() {
        const {value} = this.input.current;
        const valueAsNumber = convert(value);
        if (this.props.type === 'number') {
            this.setPropValue(
                this.props.value,
                isNil(valueAsNumber) ? value : valueAsNumber
            );
        } else {
            this.props.setProps({value});
        }
    }

    onKeyPress(e) {
        if (e.key === 'Enter') {
            this.props.setProps({
                n_submit: this.props.n_submit + 1,
                n_submit_timestamp: Date.now(),
            });
            this.input.current.checkValidity();
        }
        return this.props.debounce && e.key === 'Enter' && this.onEvent();
    }

    onChange() {
        if (!this.props.debounce) {
            this.onEvent();
        } else if (this.props.type !== 'number') {
            this.setState({value: this.input.current.value});
        }
    }
}

MyPersistedComponentNested.defaultProps = {
    type: 'text',
    n_submit: 0,
    n_submit_timestamp: -1,
    debounce: false,
    persisted_props: ['value.nested_value'],
    persistence_type: 'local',
};

MyPersistedComponentNested.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,

    /**
     * The value of the input
     */
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),

    /**
     * The input's inline styles
     */
    style: PropTypes.object,

    /**
     * The class of the input element
     */
    className: PropTypes.string,

    /**
     * If true, changes to input will be sent back to the Dash server only on enter or when losing focus.
     * If it's false, it will sent the value back on every change.
     */
    debounce: PropTypes.bool,

    /**
     * The type of control to render.
     */
    type: PropTypes.oneOf([
        // Only allowing the input types with wide browser compatibility
        'text',
        'number',
        'password',
        'email',
        'range',
        'search',
        'tel',
        'url',
        'hidden',
    ]),

    /**
     * The name of the control, which is submitted with the form data.
     */
    name: PropTypes.string,

    /**
     * A regular expression that the control's value is checked against. The pattern must match the entire value, not just some subset. Use the title attribute to describe the pattern to help the user. This attribute applies when the value of the type attribute is text, search, tel, url, email, or password, otherwise it is ignored. The regular expression language is the same as JavaScript RegExp algorithm, with the 'u' parameter that makes it treat the pattern as a sequence of unicode code points. The pattern is not surrounded by forward slashes.
     */
    pattern: PropTypes.string,

    /**
     * A hint to the user of what can be entered in the control . The placeholder text must not contain carriage returns or line-feeds. Note: Do not use the placeholder attribute instead of a <label> element, their purposes are different. The <label> attribute describes the role of the form element (i.e. it indicates what kind of information is expected), and the placeholder attribute is a hint about the format that the content should take. There are cases in which the placeholder attribute is never displayed to the user, so the form must be understandable without it.
     */
    placeholder: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),

    /**
     * Number of times the `Enter` key was pressed while the input had focus.
     */
    n_submit: PropTypes.number,
    /**
     * Last time that `Enter` was pressed.
     */
    n_submit_timestamp: PropTypes.number,

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
    persisted_props: PropTypes.arrayOf(PropTypes.oneOf(['value.nested_value'])),

    /**
     * Where persisted user changes will be stored:
     * memory: only kept in memory, reset on page refresh.
     * local: window.localStorage, data is kept after the browser quit.
     * session: window.sessionStorage, data is cleared once the browser quit.
     */
    persistence_type: PropTypes.oneOf(['local', 'session', 'memory']),
};

MyPersistedComponentNested.persistenceTransforms = {
    value: {

      nested_value: {

          extract: propValue => {
              if (!(propValue === null || propValue === undefined)) {
                  return propValue.toUpperCase();
              }
              return propValue;
          },
          apply: storedValue => storedValue,

      }

  },
};

