import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux'
import {getReloadHash} from "../../actions/api";

class Reloader extends React.Component {
    constructor(props) {
        super(props);
        if (props.config.hot_reload) {
            const { hash, interval } = props.config.hot_reload;
            this.state = {
                hash: hash,
                interval
            }
        } else {
            this.state = {
                disabled: true
            }
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
        const { disabled, interval } = this.state;
        if (!disabled) {
            setInterval(() => {
                dispatch(getReloadHash())
            }, interval);
        }
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
 