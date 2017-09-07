import {connect} from 'react-redux'
import {isEmpty} from 'ramda'
import React, {PropTypes} from 'react'

function Loading(props) {
    if (!isEmpty(props.requestQueue)) {
        return (
            <div className="_dash-loading-callback"/>
        )
    } else {
        return null;
    }
}

Loading.propTypes = {
    requestQueue: PropTypes.array.required
}

export default connect(
    state => ({
        requestQueue: state.requestQueue
    })
)(Loading);
