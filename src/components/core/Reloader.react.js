import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux'
import {getReloadHash} from "../../actions/api";

class Reloader extends React.Component {
    constructor(props) {
        super(props);
        if (props.config.hot_reload) {
            const { interval } = props.config.hot_reload;
            this.state = {
                hash: null,
                interval,
                disabled: false,
                intervalId: null
            }
        } else {
            this.state = {
                disabled: true
            }
        }
    }

    componentDidUpdate() {
        const {reloadRequest, dispatch} = this.props;
        if (reloadRequest.status === 200) {
            if (this.state.hash === null) {
                this.setState({hash: reloadRequest.content.reloadHash});
                return;
            }
            if (reloadRequest.content.reloadHash !== this.state.hash) {
                // eslint-disable-next-line no-undef
                window.clearInterval(this._intervalId);
                if (reloadRequest.content.hard) {
                    // Assets file have changed, need to reload them.
                    // eslint-disable-next-line no-undef
                    window.top.location.reload();
                } else {
                    // Py file has changed, just rebuild the reducers.
                    dispatch({'type': 'RELOAD'});
                }
            }
        }
    }

    componentDidMount() {
        const { dispatch } = this.props;
        const { disabled, interval } = this.state;
        if (!disabled && !this.state.intervalId) {
            const intervalId = setInterval(() => {
                dispatch(getReloadHash());
            }, interval);
            this.setState({intervalId})
        }
    }

    componentWillUnmount() {
        if (!this.state.disabled && this.state.intervalId) {
            // eslint-disable-next-line no-undef
            window.clearInterval(this.state.intervalId);
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
    reloadRequest: PropTypes.object,
    dispatch: PropTypes.func,
    interval: PropTypes.number
};

export default connect(
    state => ({
        config: state.config,
        reloadRequest: state.reloadRequest
    }),
    dispatch => ({dispatch})
)(Reloader);
 