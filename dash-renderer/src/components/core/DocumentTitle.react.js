import {connect} from 'react-redux';
import {Component} from 'react';
import PropTypes from 'prop-types';
import {isEmpty} from 'ramda';

class DocumentTitle extends Component {
    constructor(props) {
        super(props);
        this.state = {
            initialTitle: document.title,
        };
    }

    UNSAFE_componentWillReceiveProps(props) {
        if (props.isLoading) {
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
    isLoading: PropTypes.any.isRequired,
};

export default connect(state => ({
    isLoading: !isEmpty(state.loadingMap?.__dashprivate__idprops),
}))(DocumentTitle);
