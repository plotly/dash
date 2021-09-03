import PropTypes from 'prop-types';
import {Component} from 'react';

/**
 * ConfirmDialog is used to display the browser's native "confirm" modal,
 * with an optional message and two buttons ("OK" and "Cancel").
 * This ConfirmDialog can be used in conjunction with buttons when the user
 * is performing an action that should require an extra step of verification.
 */
export default class ConfirmDialog extends Component {
    componentDidUpdate(prevProps) {
        this._update(!prevProps.displayed && this.props.displayed);
    }

    componentDidMount() {
        this._update(this.props.displayed);
    }

    _update(shouldTriggerDisplay) {
        const {message, setProps, cancel_n_clicks, submit_n_clicks} =
            this.props;

        if (shouldTriggerDisplay) {
            new Promise(resolve => resolve(window.confirm(message))).then(
                result => {
                    if (result) {
                        setProps({
                            submit_n_clicks: submit_n_clicks + 1,
                            submit_n_clicks_timestamp: Date.now(),
                            displayed: false,
                        });
                    } else {
                        setProps({
                            cancel_n_clicks: cancel_n_clicks + 1,
                            cancel_n_clicks_timestamp: Date.now(),
                            displayed: false,
                        });
                    }
                }
            );
        }
    }

    render() {
        return null;
    }
}

ConfirmDialog.defaultProps = {
    submit_n_clicks: 0,
    submit_n_clicks_timestamp: -1,
    cancel_n_clicks: 0,
    cancel_n_clicks_timestamp: -1,
};

ConfirmDialog.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,

    /**
     * Message to show in the popup.
     */
    message: PropTypes.string,
    /**
     * Number of times the submit button was clicked
     */
    submit_n_clicks: PropTypes.number,
    /**
     * Last time the submit button was clicked.
     */
    submit_n_clicks_timestamp: PropTypes.number,
    /**
     * Number of times the popup was canceled.
     */
    cancel_n_clicks: PropTypes.number,
    /**
     * Last time the cancel button was clicked.
     */
    cancel_n_clicks_timestamp: PropTypes.number,
    /**
     *  Set to true to send the ConfirmDialog.
     */
    displayed: PropTypes.bool,

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    setProps: PropTypes.func,
};
