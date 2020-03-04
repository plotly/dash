import {connect} from 'react-redux';
import {any} from 'ramda';
import {Component} from 'react';
import PropTypes from 'prop-types';

class DocumentTitle extends Component {
    constructor(props) {
        super(props);
        this.state = {
            initialTitle: document.title,
        };
    }

    UNSAFE_componentWillReceiveProps(props) {
        if (any(r => r.status === 'loading', props.requestQueue)) {
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
    requestQueue: PropTypes.array.isRequired,
};

export default connect(state => ({
    requestQueue: state.requestQueue,
}))(DocumentTitle);
