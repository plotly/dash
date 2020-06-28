import {connect} from 'react-redux';
import {Component} from 'react';
import PropTypes from 'prop-types';

class DocumentTitle extends Component {
    constructor(props) {
        super(props);
        const {update_title} = props.config;
        this.state = {
            initialTitle: document.title,
            update_title: update_title,
        };
    }

    UNSAFE_componentWillReceiveProps(props) {
        if (props.pendingCallbacks.length) {
            document.title = this.state.update_title;
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
    update_title: PropTypes.string,
};

export default connect(state => ({
    config: state.config,
    pendingCallbacks: state.pendingCallbacks,
}))(DocumentTitle);
