import React from 'react';
import PropTypes from 'prop-types';

import './css/logout.css';

/**
 * Logout button to submit a form post request to the `logout_url` prop.
 * Usage is intended for dash-deployment-server authentication.
 *
 * DDS usage:
 *
 * `dcc.LogoutButton(logout_url=os.getenv('DASH_LOGOUT_URL'))`
 *
 * Custom usage:
 *
 * - Implement a login mechanism.
 * - Create a flask route with a post method handler.
 * `@app.server.route('/logout', methods=['POST'])`
 *   - The logout route should perform what's necessary for the user to logout.
 *   - If you store the session in a cookie, clear the cookie:
 *   `rep = flask.Response(); rep.set_cookie('session', '', expires=0)`
 *
 * - Create a logout button component and assign it the logout_url
 * `dcc.LogoutButton(logout_url='/logout')`
 *
 * See https://dash.plotly.com/dash-core-components/logout_button
 * for more documentation and examples.
 */
export default class LogoutButton extends React.Component {
    render() {
        const {id, logout_url, label, className, style, method, loading_state} =
            this.props;

        let url, submitMethod;
        if (!logout_url) {
            url =
                logout_url ||
                'https://dash.plotly.com/dash-core-components/logout_button';
            submitMethod = 'get';
        } else {
            url = logout_url;
            submitMethod = method;
        }

        return (
            <form
                data-dash-is-loading={
                    (loading_state && loading_state.is_loading) || undefined
                }
                action={url}
                method={submitMethod}
                className="dash-logout-frame"
            >
                <button
                    className={`dash-logout-btn ${className || ''}`}
                    style={style}
                    id={id}
                    type="submit"
                >
                    {label}
                </button>
            </form>
        );
    }
}

LogoutButton.defaultProps = {
    label: 'Logout',
    method: 'post',
};

LogoutButton.propTypes = {
    /**
     * Id of the button.
     */
    id: PropTypes.string,

    /**
     * Text of the button
     */
    label: PropTypes.string,
    /**
     * Url to submit a post logout request.
     */
    logout_url: PropTypes.string,
    /**
     * Style of the button
     */
    style: PropTypes.object,
    /**
     * Http method to submit the logout form.
     */
    method: PropTypes.string,
    /**
     * CSS class for the button.
     */
    className: PropTypes.string,
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
};
