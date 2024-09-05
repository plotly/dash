import {Component} from 'react';
import PropTypes from 'prop-types';

/**
 * The CurrentLocation component gets geolocation of the device from the web browser.  See more info here:
 * https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API
 */

export default class Geolocation extends Component {
    constructor(props) {
        super(props);
        this.success = this.success.bind(this);
        this.error = this.error.bind(this);
    }
    updatePosition() {
        if (this.props.update_now) {
            this.props.setProps({
                update_now: false,
            });
        }
        if (!navigator.geolocation) {
            this.error({
                code: 999,
                message: 'Your browser does not support Geolocation',
            });
        } else {
            const positionOptions = {
                enableHighAccuracy: this.props.high_accuracy,
                maximumAge: this.props.maximum_age,
                timeout: this.props.timeout,
            };

            navigator.geolocation.getCurrentPosition(
                this.success,
                this.error,
                positionOptions
            );
        }
    }

    componentDidMount() {
        this.updatePosition();
    }

    componentDidUpdate(prevProps) {
        if (
            this.props.update_now ||
            prevProps.maximum_age !== this.props.maximum_age ||
            prevProps.timeout !== this.props.timeout ||
            prevProps.high_accuracy !== this.props.high_accuracy
        ) {
            this.updatePosition();
        }
    }

    success(pos) {
        const crd = pos.coords;
        const position_obj = {
            lat: crd.latitude ?? null,
            lon: crd.longitude ?? null,
            accuracy: crd.accuracy ?? null,
            alt: crd.altitude ?? null,
            alt_accuracy: crd.altitudeAccuracy ?? null,
            speed: crd.speed ?? null,
            heading: crd.heading ?? null,
        };

        this.props.setProps({
            local_date: new Date(pos.timestamp).toLocaleString(),
            timestamp: pos.timestamp,
            position: position_obj,
            position_error: null,
        });
    }

    error(err) {
        if (this.props.show_alert) {
            alert(`ERROR(${err.code}): ${err.message}`);
        }
        this.props.setProps({
            position: null,
            position_error: {
                code: err.code,
                message: err.message,
            },
        });
    }

    render() {
        return null;
    }
}

Geolocation.defaultProps = {
    update_now: false,
    high_accuracy: false,
    position_error: null,
    maximum_age: 0,
    timeout: Infinity,
    show_alert: false,
};

Geolocation.propTypes = {
    /**
     * The ID used to identify this component in Dash callbacks.
     */
    id: PropTypes.string,

    /**
     * The local date and time when the device position was updated.
     * Format:  MM/DD/YYYY, hh:mm:ss p   where p is AM or PM
     */
    local_date: PropTypes.string,

    /**
     * The Unix timestamp from when the position was updated
     */
    timestamp: PropTypes.number,

    /**
     * The position of the device.  `lat`, `lon`, and `accuracy` will always be returned.  The other data will be included
     * when available, otherwise it will be NaN.
     *
     *       `lat` is latitude in degrees.
     *       `lon` is longitude in degrees.
     *       `accuracy` is the accuracy of the lat/lon in meters.    *
     *
     *       `alt` is altitude above mean sea level in meters.
     *       `alt_accuracy` is the accuracy of the altitude  in meters.
     *       `heading` is the compass heading in degrees.
     *       `speed` is the  speed in meters per second.
     *
     */
    position: PropTypes.shape({
        lat: PropTypes.number,
        lon: PropTypes.number,
        accuracy: PropTypes.number,
        alt: PropTypes.number,
        alt_accuracy: PropTypes.number,
        heading: PropTypes.number,
        speed: PropTypes.number,
    }),

    /**
     *  Position error
     */
    position_error: PropTypes.shape({
        code: PropTypes.number,
        message: PropTypes.string,
    }),

    /**
     * If true, error messages will be displayed as an alert
     */
    show_alert: PropTypes.bool,

    /**
     *  Forces a one-time update of the position data.   If set to True in a callback, the browser
     *   will update the position data and reset update_now back to False.  This can, for example, be used to update the
     *  position with a button or an interval timer.
     */
    update_now: PropTypes.bool,

    /**
     *  If true and if the device is able to provide a more accurate position,
     *  it will do so. Note that this can result in slower response times or increased power consumption (with a GPS
     *  chip on a mobile device for example). If false (the default value), the device can save resources by
     *  responding more quickly and/or using less power.
     */
    high_accuracy: PropTypes.bool,

    /**
     * The maximum age in milliseconds of a possible cached position that is acceptable to return. If set to 0,
     * it means that the device cannot use a cached position and must attempt to retrieve the real current position.
     * If set to Infinity the device must return a cached position regardless of its age. Default: 0.
     */
    maximum_age: PropTypes.number,

    /**
     * The maximum length of time (in milliseconds) the device is allowed to take in order to return a position.
     * The default value is Infinity, meaning that data will not be return until the position is available.
     */
    timeout: PropTypes.number,

    /**
     * Dash-assigned callback that should be called to report property changes
     * to Dash, to make them available for callbacks.
     */
    setProps: PropTypes.func,
};
