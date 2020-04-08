import {connect} from 'react-redux';
import React from 'react';
import PropTypes from 'prop-types';

function Loading(props) {
    if (props.pendingCallbacks.length) {
        return <div className="_dash-loading-callback" />;
    }
    return null;
}

Loading.propTypes = {
    pendingCallbacks: PropTypes.array.isRequired,
};

export default connect(state => ({
    pendingCallbacks: state.pendingCallbacks,
}))(Loading);
