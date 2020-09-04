import React, {PureComponent} from 'react';
import PropTypes from 'prop-types';

const isEquivalent = (v1, v2) => v1 === v2 || (isNaN(v1) && isNaN(v2));

const omit = (key, obj) => {
    const { [key]: omitted, ...rest } = obj;
    return rest;
  }

/**
 * Adapted dcc input component for persistence tests.
 *
 * Note that unnecessary props have been removed.
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
        this.setInputValue(
            value,
            nextProps.value
        );
        this.setState({value: nextProps.value});
    }

    componentDidMount() {
        const {value} = this.input.current;
        this.setInputValue(
            value,
            this.props.value
        );
    }

    UNSAFE_componentWillMount() {
        this.setState({value: this.props.value})
    }

    render() {
        const valprops = {value: this.state.value}
        return (
            <input
                ref={this.input}
                onChange={this.onChange}
                onKeyPress={this.onKeyPress}
                {...valprops}
                {...omit(
                    [
                        'value',
                        'setProps',
                    ],
                    this.props
                )}
            />
        );
    }

    setInputValue(base, value) {
        base = NaN;

        if (!isEquivalent(base, value)) {
            this.input.current.value = value
        }
    }

    setPropValue(base, value) {
        if (!isEquivalent(base, value)) {
            this.props.setProps({value});
        }
    }

    onEvent() {
        const {value} = this.input.current;
        this.props.setProps({value})
    }

    onKeyPress(e) {
        return this.onEvent();
    }

    onChange() {
        this.onEvent()
    }
}

MyPersistedComponentNested.defaultProps = {
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
     * The name of the control, which is submitted with the form data.
     */
    name: PropTypes.string,

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
