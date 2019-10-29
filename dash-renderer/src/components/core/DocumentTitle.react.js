/* global document:true */

import {connect} from 'react-redux';
import {Component} from 'react';
import PropTypes from 'prop-types';

class DocumentTitle extends Component {
    constructor(props) {
        super(props);
        this.state = {
            initialTitle: document.title,
        };
    }

    componentWillReceiveProps(props) {
        if (props.pendingCallbacks.length) {
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

DocumentTitle.propTypes = {
    pendingCallbacks: PropTypes.array.isRequired,
};

export default connect(state => ({
    pendingCallbacks: state.pendingCallbacks,
}))(DocumentTitle);
