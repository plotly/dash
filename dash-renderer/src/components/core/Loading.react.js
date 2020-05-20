import {connect} from 'react-redux';
import React from 'react';
import PropTypes from 'prop-types';
import {isEmpty} from 'ramda';

function Loading(props) {
    if (props.isLoading) {
        return <div className="_dash-loading-callback" />;
    }
    return null;
}

Loading.propTypes = {
    isLoading: PropTypes.any.isRequired,
};

export default connect(state => ({
    isLoading: !isEmpty(state.loadingMap?.__dashprivate__idprops),
}))(Loading);
