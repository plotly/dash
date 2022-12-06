import {includes, isEmpty} from 'ramda';
import PropTypes from 'prop-types';
import React, {Component} from 'react'; // eslint-disable-line no-unused-vars
import prettyMilliseconds from 'pretty-ms';

function getFormat(format_type) {
    const formats = {
        default: {},
        verbose: {verbose: true},
        colons: {colonNotation: true},
        compact: {compact: true},
        sub_ms: {formatSubMilliseconds: true},
    };
    return formats[format_type];
}

/**
 * The Timer component has all the functionality of the Interval component plus
 * the following additional features:
 *
 * Operate in either `countdown` or `stopwatch` (count up) modes.
 * Display custom messages, or start/stop jobs at specified times.
 * Convert milliseconds into human readable times.
 * Update messages clientside to help improve app performance.
 * Specify the elapsed times to fire a callback rather than every interval
 **/

export default class Timer extends Component {
    constructor(props) {
        super(props);
        this.intervalId = null;
        this.renderMessage = null;
        this.intervalError = false;
        this.handleIntervalError = this.handleIntervalError.bind(this);
        this.displayIntervalErrorMessage =
            this.displayIntervalErrorMessage.bind(this);
        this.reportInterval = this.reportInterval.bind(this);
        this.handleTimer = this.handleTimer.bind(this);
        this.handleMessages = this.handleMessages.bind(this);
    }

    handleTimer() {
        const {
            n_intervals,
            max_intervals,
            disabled,
            rerun,
            interval,
            time,
            mode,
            duration,
        } = this.props;

        // Check if timer should stop or shouldn't even start
        if (
            max_intervals === 0 ||
            disabled ||
            (n_intervals >= max_intervals && max_intervals !== -1) ||
            duration === 0 ||
            duration < 0 ||
            (mode === 'countdown' && duration === null) || // operates as stopwatch if duration is null
            (mode === 'countdown' && time === 0 && !rerun) ||
            (mode === 'stopwatch' && time === duration && !rerun) ||
            this.intervalError
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
            if (
                (mode === 'countdown' && time === 0 && rerun) ||
                (mode === 'stopwatch' && time === duration && rerun)
            ) {
                this.initTimer();
            }
            return;
        }

        // it hasn't started yet (& it should start)
        this.intervalId = window.setInterval(this.reportInterval, interval);
    } // end handle timer

    handleMessages(time) {
        const {messages, timer_format} = this.props;

        const messagesObj = Object.assign({}, messages);
        if (time in messagesObj) {
            this.renderMessage = messagesObj[time];
        }

        if (timer_format !== 'none' && isEmpty(messagesObj)) {
            const formatObj = getFormat(timer_format);
            this.renderMessage = prettyMilliseconds(time, formatObj);
        }
    } // end handleMessages

    reportInterval() {
        const {setProps, n_intervals, interval, mode, duration, fire_times} =
            this.props;

        const new_n_intervals = n_intervals + 1;
        const updateProps = {n_intervals: new_n_intervals};

        let new_time;
        new_time = duration > 0 ? duration - interval * new_n_intervals : 0;
        if (
            mode === 'stopwatch' ||
            duration === null ||
            duration === undefined
        ) {
            new_time = interval * new_n_intervals;
        }

        this.handleMessages(new_time);
        updateProps.time = new_time;

        if (includes(new_time, fire_times)) {
            updateProps.at_fire_time = new_time;
        }
        setProps(updateProps);
    } // end report interval

    initTimer() {
        const {setProps, duration, mode} = this.props;

        let startTime;
        if (mode === 'countdown' && duration > 0) {
            startTime = duration;
        } else {
            // stopwatch
            startTime = 0;
        }
        this.handleMessages(startTime);

        setProps({
            n_intervals: 0,
            reset: false,
            time: startTime,
        });
    }

    resetTimer() {
        this.handleIntervalError();
        this.clearTimer();
        this.initTimer();
        this.handleTimer();
    }

    clearTimer() {
        window.clearInterval(this.intervalId);
        this.intervalId = null;
    }

    displayIntervalErrorMessage(timeError) {
        this.intervalError = true;
        throw new Error(
            timeError +
                ' is not a multiple of the interval (' +
                this.props.interval +
                ')'
        );
    }

    handleIntervalError() {
        const {interval, duration, messages, fire_times} = this.props;
        this.intervalError = false;

        // check if times are a multiple of the interval
        const isIntervalError = timeVal => timeVal % interval > 0;

        if (isIntervalError(duration)) {
            this.displayIntervalErrorMessage(
                'The Timer duration (' + duration + ')'
            );
        }

        if (Array.isArray(fire_times) && fire_times.length) {
            if (fire_times.some(isIntervalError)) {
                this.displayIntervalErrorMessage(
                    'One or more of the Timer fire_times'
                );
            }
        }

        const msgObj = Object.assign({}, messages);
        if (Object.keys(msgObj).some(isIntervalError)) {
            this.displayIntervalErrorMessage(
                'One or more of the keys in the Timer messages dictionary '
            );
        }
    }

    componentDidMount() {
        this.initTimer();
        this.handleTimer();
    }

    componentDidUpdate(prevProps) {
        if (
            prevProps.interval !== this.props.interval ||
            prevProps.duration !== this.props.duration ||
            prevProps.max_intervals !== this.props.max_intervals ||
            prevProps.reset !== this.props.reset ||
            prevProps.rerun !== this.props.rerun ||
            prevProps.messages !== this.props.messages ||
            prevProps.mode !== this.props.mode
        ) {
            this.resetTimer();
        } else {
            this.handleTimer();
        }
    }

    componentWillUnmount() {
        this.clearTimer();
    }

    render() {
        const {id, className, style} = this.props;
        return (
            <div id={id} style={style} className={className}>
                <div>{this.renderMessage}</div>
            </div>
        );
    }
}

Timer.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks.
     */
    id: PropTypes.string,

    /**
     * This component will increment the counter `n_intervals` every `interval` milliseconds.
     */
    interval: PropTypes.number,

    /**
     * If True, the n_interval counter and the timer no longer updates. This pauses the timer.
     */
    disabled: PropTypes.bool,

    /**
     * Number of times the interval has passed (read-only)
     */
    n_intervals: PropTypes.number,

    /**
     * Number of times the interval will be fired.
     * If -1, then the interval has no limit (the default)
     * and if 0 then the interval stops running.
     */
    max_intervals: PropTypes.number,

    /**
     * When in countdown mode, the timer will count down to zero from the starting `duration` and will show the number
     *  of milliseconds remaining.
     *  When in stopwatch mode, the timer will count up from zero and show the number of milliseconds elapsed.
     *  (read-only)
     */
    time: PropTypes.number,

    /**
     * The timer will count down to zero in `countdown` mode and count up from zero in `stopwatch` mode.
     */
    mode: PropTypes.oneOf(['stopwatch', 'countdown']),

    /**
     * Sets the number of milliseconds the timer will run. A duration > 0 is required for the countdown timer to run.
     * If 0 then the timer will not start.
     */
    duration: PropTypes.number,

    /**
     * This will start the timer at the beginning with the given prop settings.
     */
    reset: PropTypes.bool,

    /**
     * A list of the time(s) in milliseconds at which to fire a callback. Each time must be a multiple of the interval.
     */
    fire_times: PropTypes.arrayOf(PropTypes.number),

    /**
     * This is updated when the timer reaches one of the times in the `fire_times` list. Using `at_fire_time` in a
     * callback will trigger the callback at the time(s) in `fire_times` (Read only).
     */
    at_fire_time: PropTypes.number,

    /**
     * When True, the timer repeats once the timer has run for the number of milliseconds set in the duration.
     */
    rerun: PropTypes.bool,

    /**
     * A dictionary in the form of: {integer: string} where integer is a time in milliseconds and string is the
     * message to display upon reaching that time. Note - `messages` overrides any other timer display.
     */
    messages: PropTypes.objectOf(PropTypes.string),

    /**
     * This formats the timer (milliseconds) into human readable formats.  The options are:
     *  `'none'`: no timer will be displayed;
     *  `'default'`:  example - 1337000000 milliseconds will display as: '15d 11h 23m 20s';
     *  `'compact'`: will show only the first unit: 1h 10m --> 1h ;
     *  `'verbose'`: will show full-length units. Example --  5 hours 1 minute 45 seconds
     *  `'colons'`: Useful when you want to show time without the time units, similar to a digital watch.
     *   Will always shows time in at least minutes: 1s --> 0:01. Example - 5h 1m 45s --> 5:01:45.
     *  `'sub_ms'`:  will display sub milliseconds. Example 1800 milliseconds will display as '1s 800ms'
     */
    timer_format: PropTypes.oneOf([
        'none',
        'default',
        'compact',
        'verbose',
        'colons',
        'sub_ms',
    ]),

    /**
     * The messages styles
     */
    style: PropTypes.object,

    /**
     * The class  name of the messages container
     */
    className: PropTypes.string,

    /**
     * Dash assigned callback
     */
    setProps: PropTypes.func,
};

Timer.defaultProps = {
    interval: 1000,
    n_intervals: 0,
    max_intervals: -1,
    duration: null,
    time: 0,
    mode: 'stopwatch',
    reset: true,
    rerun: false,
    messages: {},
    fire_times: [],
    at_fire_time: null,
    timer_format: 'default',
};
