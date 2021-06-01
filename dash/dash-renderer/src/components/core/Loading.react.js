import {connect} from 'react-redux';
import React from 'react';
import PropTypes from 'prop-types';

function Loading(props) {
    if (props.isLoading) {
        return <div className='_dash-loading-callback' />;
    }
    return null;
}

Loading.propTypes = {
    isLoading: PropTypes.bool.isRequired
};

export default connect(state => ({
    isLoading: state.isLoading
}))(Loading);
