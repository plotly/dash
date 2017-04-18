/* global window:true */
import React, {Component, PropTypes} from 'react';
import {connect} from 'react-redux'
import queryString from 'query-string';
import {getConfig, login} from './actions/api';
import {contains, isEmpty} from 'ramda'

const CLOUD = 'cloud';
const ONPREM = 'onprem';
const SERVER_TYPES = {
    [CLOUD]: 'Plotly Cloud',
    [ONPREM]: 'Plotly On-Premise'
};

// TODO - Somehow figure out a variable redirect_uri
// and require app creators to set this
const REDIRECT_URI_PATHNAME = '/oauth2/callback'
const REDIRECT_URI = `http://localhost:9595${REDIRECT_URI_PATHNAME}`;

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
class Login extends Component {
    constructor(props) {
        super(props);
        this.state = {
            domain: '',
            statusMessasge: '',
            serverType: CLOUD,
            status: '',
            username: ''
        };
        this.authenticateUser = this.authenticateUser.bind(this);
        this.buildOauthUrl = this.buildOauthUrl.bind(this);
        this.oauthPopUp = this.oauthPopUp.bind(this);
        this.verifyAuthDone = this.verifyAuthDone.bind(this);
    }

    buildOauthUrl() {
        const oauthClientId = 'RcXzjux4DGfb8bWG9UNGpJUGsTaS0pUVHoEf7Ecl';
        const isOnPrem = this.state.serverType === ONPREM;
        const plotlyDomain = isOnPrem ? this.state.domain : 'https://plot.ly';
        return (
            `${plotlyDomain}/o/authorize/?response_type=token&` +
            `client_id=${oauthClientId}&` +
            `redirect_uri=${REDIRECT_URI}`
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

    verifyAuthDone() {
        return false;
    }

    authenticateUser () {
        if (!this.state.domain && this.state.serverType === ONPREM) {
            this.setState({
                status: 'failure',
                statusMessasge: 'Enter your Plotly On Premise domain.'
            });
            return;
        }
        this.setState({statusMessasge: ''});
        this.oauthPopUp();
    }

    render() {
        const renderOption = (value) => {
            const selected = this.state.serverType === value;
            return (
                <span>
                    <button
                        className={selected ? 'button-primary' : 'button'}
                        onClick={(e) => this.setState({serverType: e.target.value})}
                        value={value}
                        style={{margin: '10px'}}
                    >{SERVER_TYPES[value]}</button>
                </span>
            );
        };

        const loginButton = (
            <button
                className="btn btn-large btn-primary"
                style={{display: 'block', margin: 'auto'}}
                onClick={() => this.authenticateUser()}
            >{'Login'}</button>
        );

        const serverTypeOptions = (
            <div className="control-group">
            <h3 className="block-center-heading">
                {'I am connecting to...'}
            </h3>
                <div className="controls" style={{padding: '20px'}}>
                    {renderOption(CLOUD)}
                    {renderOption(ONPREM)}
                </div>
                <span style={{borderBottom: '2px solid #E7E8E9', cursor: 'pointer'}}>
                    <a href='https://plot.ly/products/cloud/'>
                        Learn more about our products.
                    </a>
                </span>
            </div>
        );

        const loginCloud = (
            <div className="control-group">
                <h3 className="block-center-heading">{'Plotly Log In'}</h3>
                <div className="controls" style={{padding: '20px'}}>
                    <div className="form-group">
                        {loginButton}
                    </div>
                </div>
            </div>
        );

        const loginOnPrem = (
            <div className="control-group">
                <h3 className="block-center-heading">{'Login Into Your Account'}</h3>
                <div className="controls" style={{padding: '20px'}}>
                    <div className="form-group">
                        <label>Your On-Prem Plotly Domain</label>
                        <input
                            type="text"
                            className="form-control"
                            placeholder="https://plotly.your-company.com"
                            onChange={(e) => this.setState({domain: e.target.value})}
                        ></input>
                        {loginButton}
                    </div>
                </div>
            </div>
        );

        const loginOptions = {
            cloud: loginCloud,
            onprem: loginOnPrem
        };

        return (
            <div className="container">
                <div className="block-center">
                    <div style={{textAlign: 'center'}}>
                        {serverTypeOptions}
                    </div>
                    <div style={{textAlign: 'center'}}>
                        {loginOptions[this.state.serverType]}
                    </div>
                    <div style={{textAlign: 'center'}}>
                        {this.state.statusMessasge}
                    </div>
                </div>
            </div>
        );
    }
}
Login.propTypes = {
    onClosed: PropTypes.func
}

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

            content = 'Loading...';

        } else if (loginRequest.status === 200) {
            // TODO - close this window automatically
            content = 'Logged in. You may now close this window.';

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
        const {configRequest, dispatch} = props
        if (isEmpty(configRequest)) {
            // TODO - Could do request in parallel
            dispatch(getConfig());
        }
    }

    render() {

        const {children, configRequest} = this.props;

        // OAuth redirect
        if (window.location.pathname === REDIRECT_URI_PATHNAME) {
            return (
                <OauthRedirect/>
            );
        }

        if (isEmpty(configRequest) || configRequest.status === 'loading') {

            return <div>Loading...</div>

        }

        else if (configRequest.status !== 200) {

            return <div>Error loading configuration.</div>

        }

        else if (configRequest.content.fid) {

            // TODO - different tokens for on-prem vs cloud
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
    configRequest: PropTypes.object
}

export default connect(
    state => ({
        configRequest: state.configRequest,
    }),
    dispatch => ({dispatch})
)(Authentication);
