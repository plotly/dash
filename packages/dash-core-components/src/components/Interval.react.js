import PropTypes from 'prop-types';
import React, {Component} from 'react'; // eslint-disable-line no-unused-vars

/**
 * A component that repeatedly increments a counter `n_intervals`
 * with a fixed time delay between each increment.
 * Interval is good for triggering a component on a recurring basis.
 * The time delay is set with the property "interval" in milliseconds.
 */
export default class Interval extends Component {
    constructor(props) {
        super(props);
        this.intervalId = null;
        this.reportInterval = this.reportInterval.bind(this);
        this.handleTimer = this.handleTimer.bind(this);
    }

    handleTimer(props) {
        // Check if timer should stop or shouldn't even start
        if (
            props.max_intervals === 0 ||
            props.disabled ||
            (props.n_intervals >= props.max_intervals &&
                props.max_intervals !== -1)
        ) {
            // stop existing timer
            if (this.intervalId) {
                this.clearTimer();
            }
            // and don't start a timer
            return;
        }

        // keep the existing timer running
        if (this.intervalId) {
            return;
        }

        // it hasn't started yet (& it should start)
        this.intervalId = window.setInterval(
            this.reportInterval,
            props.interval
        );
    }

    resetTimer(props) {
        this.clearTimer();
        this.handleTimer(props);
    }

    clearTimer() {
        window.clearInterval(this.intervalId);
        this.intervalId = null;
    }

    reportInterval() {
        const {setProps, n_intervals} = this.props;
        setProps({n_intervals: n_intervals + 1});
    }

    componentDidMount() {
        this.handleTimer(this.props);
    }

    UNSAFE_componentWillReceiveProps(nextProps) {
        if (nextProps.interval !== this.props.interval) {
            this.resetTimer(nextProps);
        } else {
            this.handleTimer(nextProps);
        }
    }

    componentWillUnmount() {
        this.clearTimer();
    }

    render() {
        return null;
    }
}

Interval.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,
    /**
     * This component will increment the counter `n_intervals` every
     * `interval` milliseconds
     */
    interval: PropTypes.number,

    /**
     * If True, the counter will no longer update
     */
    disabled: PropTypes.bool,

    /**
     * Number of times the interval has passed
     */
    n_intervals: PropTypes.number,

    /**
     * Number of times the interval will be fired.
     * If -1, then the interval has no limit (the default)
     * and if 0 then the interval stops running.
     */
    max_intervals: PropTypes.number,

    /**
     * Dash assigned callback
     */
    setProps: PropTypes.func,
};

Interval.defaultProps = {
    interval: 1000,
    n_intervals: 0,
    max_intervals: -1,
};
