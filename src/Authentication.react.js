/* global window:true, document:true */
import React, {Component, PropTypes} from 'react';
import {connect} from 'react-redux'
import queryString from 'query-string';
import {login} from './actions/api';
import {readConfig} from './actions/index';
import {contains, isEmpty, merge, type} from 'ramda'
import * as styles from './styles/styles.js';
import {REDIRECT_URI_PATHNAME} from './constants/constants';

// http://stackoverflow.com/questions/4068373/center-a-popup-window-on-screen
const PopupCenter = (url, title, w, h) => {
    // Fixes dual-screen position
    const screenLeft = window.screenLeft;
    const screenTop = window.screenTop;

    const width = window.innerWidth;
    const height = window.innerHeight;

    const left = ((width / 2) - (w / 2)) + screenLeft;
    const top = ((height / 2) - (h / 2)) + screenTop;
    const popupWindow = window.open(
        url, title,
        ('scrollbars=yes,width=' + w +
         ', height=' + h + ', top=' + top +
         ', left=' + left)
    );
    return popupWindow;
};

/**
 * Login displays an interface that guides the user through an oauth flow.
 * - Clicking on a login button will launch a new window with the plot.ly
 *   oauth url
 * - plot.ly will redirect that window to defined redirect URL when complete
 * - The <OauthRedirect/> component will render the oauth redirect page
 * - When the <OauthRedirect/> window is closed, <Login/> will call its
 *   `onClosed` prop
 */
class UnconnectedLogin extends Component {
    constructor(props) {
        super(props);
        this.buildOauthUrl = this.buildOauthUrl.bind(this);
        this.oauthPopUp = this.oauthPopUp.bind(this);
    }

    buildOauthUrl() {
        const {oauth_client_id, plotly_domain} = (
            this.props.config
        );
        return (
            `${plotly_domain}/o/authorize/?response_type=token&` +
            `client_id=${oauth_client_id}&` +
            `redirect_uri=${window.location.origin}${REDIRECT_URI_PATHNAME}`
        );
    }

    oauthPopUp() {
        const popupWindow = PopupCenter(
            this.buildOauthUrl(), 'Authorization', '500', '500'
        );
        if (window.focus) {
            popupWindow.focus();
        }
        window.popupWindow = popupWindow;
        const interval = setInterval(() => {
            if(popupWindow.closed) {
                this.props.onClosed();
                clearInterval(interval);
            }
        }, 100);
    }

    render() {
        const {plotly_domain} = this.props.config;
        return (
            <div style={merge(styles.base.html, styles.base.container)}>
                <div style={styles.base.h2}>Dash</div>

                <div style={styles.base.h4}>
                    {'Log in to Plotly to continue'}
                </div>

                <button style={styles.base.button} onClick={this.oauthPopUp}>
                    {'Log in'}
                </button>

                <div style={styles.base.caption}>
                    <span>
                        {`This dash app requires a plotly login to view.
                          Don't have an account yet?`}
                    </span>
                    <a style={styles.base.a}
                       href={`${plotly_domain}/accounts/login/?action=signup`}>
                        {' Create an account '}
                    </a>
                    <span>
                    {` (it's free)
                      and then request access from the owner of this app.`}
                    </span>
                </div>
            </div>
        );
    }
}
UnconnectedLogin.propTypes = {
    onClosed: PropTypes.func,
    config: PropTypes.object
}
const Login = connect(
    state => ({config: state.config})
)(UnconnectedLogin);

/**
 * OAuth redirect component
 * - Looks for an oauth token in the URL as provided by the plot.ly redirect
 * - Make an API call to dash with that oauth token
 * - In response, Dash will set the oauth token as a cookie
 *   if it is valid
 * Parent is component is responsible for rendering
 * this component in the appropriate context
 * (the URL redirect)
 */
class UnconnectedOauthRedirect extends Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        const params = queryString.parse(window.location.hash);
        const {access_token} = params;
        const {dispatch} = this.props;
        dispatch(login(access_token));
    }

    render() {
        const {loginRequest} = this.props;
        let content;
        if (isEmpty(loginRequest) || loginRequest.status === 'loading') {

            content = <div>Loading...</div>;

        } else if (loginRequest.status === 200) {

            window.close();

        } else {

            content = (
                <div>
                    <h3>{'Yikes! An error occurred trying to log in.'}</h3>
                    {
                        loginRequest.content ?
                        <pre>{JSON.stringify(loginRequest.content)}</pre> :
                        null
                    }
                </div>
            );

        }
        return (
            <div>
                {content}
            </div>
        );
    }
}
UnconnectedOauthRedirect.propTypes = {
    loginRequest: PropTypes.object,
    login: PropTypes.func,
    dispatch: PropTypes.func
}
const OauthRedirect = connect(
    state => ({loginRequest: state.loginRequest}),
    dispatch => ({dispatch})
)(UnconnectedOauthRedirect);

/**
 * Authentication component renders the children if the user is
 * logged in or doesn't need to login.
 * Otherwise, it renders an interface that allows a user to log in.
 *
 * Log in is checked through the presence of an oauth token as a cookie.
 * Log in is only required for apps that have a `fid` in the `config`
 * API response
 *
 * Note that a user that is logged in does not necessarily have have
 * view access to the app.
 *
 * This component also renders the OAuth redirect URL
 */
class Authentication extends Component {
    constructor(props) {
        super(props);
        this.state = {
            oauth_flow_counter: 0
        }
    }

    componentDidMount() {
        this.initialization(this.props);
    }

    componentWillReceiveProps(props) {
        this.initialization(props);
    }

    initialization(props) {
        const {config, dispatch} = props;
        if (type(config) === "Null") {
            dispatch(readConfig());
        }
    }

    render() {

        const {children, config} = this.props;

        // OAuth redirect
        if (window.location.pathname === REDIRECT_URI_PATHNAME) {
            return (
                <OauthRedirect/>
            );
        }

        if (type(config) === "Null") {

            return <div>Loading...</div>;

        }

        else if (config.fid) {

            if (contains('plotly_oauth_token=', document.cookie)) {

                return children;

            }

            else {

                // Set oauth token cookie through an oauth flow
                return (
                    <Login onClosed={
                        () => this.setState({
                            oauth_flow_counter:
                            this.state.oauth_flow_counter + 1
                        })
                    }/>
                );

            }
        }

        else {

            return children;

        }
    }
}

Authentication.propTypes = {
    children: PropTypes.object,
    config: PropTypes.object
}

export default connect(
    state => ({
        config: state.config,
    }),
    dispatch => ({dispatch})
)(Authentication);
