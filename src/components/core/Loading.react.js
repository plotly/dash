import {connect} from 'react-redux'
import {isEmpty} from 'ramda'
import {Component, PropTypes} from 'react'

class Loading extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        if (!isEmpty(props.requestQueue)) {
            return (
                <div className="_dash-loading-callback"/>
            )
        } else {
            return null;
        }
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
