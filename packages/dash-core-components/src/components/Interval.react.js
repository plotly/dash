import React, {Component, PropTypes} from 'react'; // eslint-disable-line no-unused-vars

/**
 * A component that repeatedly fires an event ("interval")
 * with a fixed time delay between each event.
 * Interval is good for triggering a component on a recurring basis.
 * The time delay is set with the property "interval" in milliseconds.
 */
export default class Interval extends Component {
    constructor(props) {
        super(props);
        this.state = {};
        this.setInterval = this.setInterval.bind(this);
    }

    setInterval(props) {
        const {interval, fireEvent, setProps} = props;
        this.setState({
            intervalId: window.setInterval(() => {
                if (fireEvent && !props.disabled) {
                    fireEvent({event: 'interval'});
                }
                if (setProps && !props.disabled) {
                    setProps({n_intervals: this.props.n_intervals + 1})
                }
            }, interval)
        });
    }

    componentDidMount() {
        if (this.props.fireEvent || this.props.setProps) {
            this.setInterval(this.props);
        }
    }

    componentWillReceiveProps(nextProps) {
        if ((!this.props.fireEvent && nextProps.fireEvent) ||
            (!this.props.setProps && nextProps.setProps)) {
            this.setInterval(nextProps);
        } else if (
            this.props.interval !== nextProps.interval &&
            this.state.intervalId
        ) {
            window.clearInterval(this.state.intervalId);
            this.setInterval(nextProps);
        }
    }

    componentWillUnmount() {
        window.clearInterval(this.state.intervalId);
    }

    render() {
        return null;
    }
}

Interval.propTypes = {
    id: PropTypes.string,
    /**
     * This component will fire an event every `interval`
     * milliseconds with the event name `setInterval`
     */
    interval: PropTypes.number,

    /**
    * If True, the interval will no longer trigger
    * an event.
    */
    disabled: PropTypes.bool,

    /**
     * Number of times the interval has passed
     */
    n_intervals: PropTypes.number,

    /**
     * Dash assigned callback
     */
    fireEvent: PropTypes.func,

    /**
     * Dash assigned callback
     */
    setProps: PropTypes.func,

    dashEvents: PropTypes.oneOf(['interval'])
};

Interval.defaultProps = {
    interval: 1000,
    n_intervals: 0
};
