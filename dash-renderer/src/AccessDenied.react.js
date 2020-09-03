import React from 'react';
import {mergeRight, once} from 'ramda';
import PropTypes from 'prop-types';
import * as styles from './styles/styles.js';
import * as constants from './constants/constants.js';

/* eslint-disable-next-line no-console */
const logWarningOnce = once(console.warn);

function AccessDenied(props) {
    const {config} = props;
    const fid = config.fid;
    const owner_username = fid.split(':')[0];
    return (
        <div style={mergeRight(styles.base.html, styles.base.container)}>
            <div style={styles.base.h2}>Access Denied</div>

            <div style={styles.base.h4}>
                Uh oh! You don't have access to this Dash app.
            </div>

            <div>
                This app is owned by {owner_username}. Reach out to
                {owner_username} to grant you access to this app and then try
                refreshing the app.
            </div>

            <br />

            <a
                style={styles.base.a}
                onClick={() => {
                    try {
                        document.cookie =
                            `${constants.OAUTH_COOKIE_NAME}=; ` +
                            'expires=Thu, 01 Jan 1970 00:00:01 GMT;';
                    } catch (e) {
                        logWarningOnce(e);
                    }
                    window.location.reload(true);
                }}
            >
                Log out of session
            </a>
        </div>
    );
}
AccessDenied.propTypes = {
    config: PropTypes.object
};
export default AccessDenied;
