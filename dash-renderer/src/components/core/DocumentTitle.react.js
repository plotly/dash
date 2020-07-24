import {connect} from 'react-redux';
import {Component} from 'react';
import PropTypes from 'prop-types';

class DocumentTitle extends Component {
    constructor(props) {
        super(props);
        const {update_title} = props.config;
        this.state = {
            title: document.title,
            update_title,
        };
    }

    UNSAFE_componentWillReceiveProps(props) {
        if (props.isLoading) {
            this.setState({title: document.title});
            if (this.state.update_title) {
                document.title = this.state.update_title;
            }
        } else {
            document.title = this.state.title;
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
    isLoading: PropTypes.bool.isRequired,
    config: PropTypes.shape({update_title: PropTypes.string}),
};

export default connect(state => ({
    isLoading: state.isLoading,
    config: state.config,
}))(DocumentTitle);
