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
        this.handleInterval = this.handleInterval.bind(this);
    }

    startTimer(props) {
        if (this.intervalId) {
            throw new Error('startTimer() invoked when timer already started');
        }

        this.intervalId = window.setInterval(
            this.handleInterval,
            props.interval
        );
    }

    resetTimer(props) {
        this.clearTimer();
        this.startTimer(props);
    }

    clearTimer() {
        window.clearInterval(this.intervalId);
        this.intervalId = null;
    }

    handleInterval() {
        const {disabled, max_intervals, n_intervals, setProps} = this.props;
        const withinMaximum =
            max_intervals === -1 || n_intervals < max_intervals;
        if (disabled || !withinMaximum) {
            return;
        }
        if (setProps) {
            setProps({n_intervals: n_intervals + 1});
        }
    }

    componentDidMount() {
        if (this.canStartTimer(this.props)) {
            this.startTimer(this.props);
        }
    }

    canStartTimer(props) {
        return props.setProps;
    }

    componentWillReceiveProps(nextProps) {
        // If we couldn't start the timer before, and we can now, start it.
        if (!this.canStartTimer(this.props) && this.canStartTimer(nextProps)) {
            this.startTimer(nextProps);
        } else if (this.props.interval !== nextProps.interval) {
            this.resetTimer(nextProps);
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
