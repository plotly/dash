import {connect} from 'react-redux';
import {any} from 'ramda';
import React from 'react';
import PropTypes from 'prop-types';

function Loading(props) {
    if (any(r => r.status === 'loading', props.requestQueue)) {
        return <div className="_dash-loading-callback" />;
    }
    return null;
}

Loading.propTypes = {
    requestQueue: PropTypes.array.isRequired,
};

export default connect(state => ({
    requestQueue: state.requestQueue,
}))(Loading);
