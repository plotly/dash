/* global document:true */

import { connect } from 'react-redux'
import { isEmpty } from 'ramda'
import React, {Component, PropTypes} from 'react'


class Loading extends Component {
    constructor(props) {
        super(props);
        this.state = {
            initialTitle: document.title
        };
    }

    componentWillReceiveProps(props) {
        if (!isEmpty(props.requestQueue)) {
            document.title = 'Updating...';
        } else {
            document.title = this.state.initialTitle;
        }
    }

    shouldComponentUpdate() {
        return false;
    }

    render() {
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
