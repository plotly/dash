import React, {PropTypes} from 'react';
import {connect} from 'react-redux'

function AccessDenied(props) {
    const {configRequest} = props;
    const fid = configRequest.content.fid;
    const owner_username = fid.split(':')[0];
    return (
        <div>
            <h3>{"Access Denied"}</h3>
            <h4>
                {"Uh oh! You don't have access to this Dash app."}
            </h4>
            <div>
                {`This app is owned by '${owner_username}'. `}
                {'Reach out to that user to grant you access then try '}
                {'refreshing the page.'}
            </div>
        </div>
    )
}
AccessDenied.propTypes = {
    configRequest: PropTypes.object
}
export default AccessDenied;
