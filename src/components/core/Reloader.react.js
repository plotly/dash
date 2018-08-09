import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux'
import {getReloadHash} from "../../actions/api";

class Reloader extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            hash: props.config.reload_hash
        }
    }

    componentDidUpdate() {
        const { reloadHash } = this.props;
        if (reloadHash.status === 200) {
            if (reloadHash.content.reloadHash !== this.state.hash) {
                // TODO add soft & hard reload option
                // soft -> rebuild the app layout (python reloaded)
                // hard -> reload the window (css/js reloaded)
                // eslint-disable-next-line no-undef
                window.top.location.reload();
            }
        }
    }

    componentDidMount() {
        const { dispatch } = this.props;
        // TODO add interval config
        setInterval(() => {
            dispatch(getReloadHash())
        }, 1000);
    }

    render() {
        return null;
    }
}

Reloader.defaultProps = {};

Reloader.propTypes = {
    id: PropTypes.string,
    config: PropTypes.object,
    reloadHash: PropTypes.object,
    dispatch: PropTypes.func
};

export default connect(
    state => ({
        config: state.config,
        reloadHash: state.reloadHash
    }),
    dispatch => ({dispatch})
)(Reloader);
 