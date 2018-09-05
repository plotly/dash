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
                reloading: false,
                disabled: false
            }
        } else {
            this.state = {
                disabled: true
            }
        }
        this._intervalId = null;
    }

    componentDidUpdate() {
        const {reloadHash, dispatch} = this.props;
        if (reloadHash.status === 200) {
            if (this.state.hash === null) {
                this.setState({hash: reloadHash.content.reloadHash});
                return;
            }
            if (reloadHash.content.reloadHash !== this.state.hash && !this.state.reloading ) {
                // eslint-disable-next-line no-undef
                window.clearInterval(this._intervalId);
                if (reloadHash.content.hard) {
                    // Assets file have changed, need to reload them.
                    // eslint-disable-next-line no-undef
                    window.top.location.reload();
                } else if (!this.state.reloading) {
                    // Py file has changed, just rebuild the reducers.
                    dispatch({'type': 'RELOAD'});
                }
            }
        }
    }

    componentDidMount() {
        const { dispatch } = this.props;
        const { disabled, interval } = this.state;
        if (!disabled && !this._intervalId) {
            this._intervalId = setInterval(() => {
                if (!this.state.reloading) {
                    dispatch(getReloadHash());
                }
            }, interval);
        }
    }

    componentWillUnmount() {
        if (!this.state.disabled) {
            // eslint-disable-next-line no-undef
            window.clearInterval(this._intervalId);
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
    dispatch: PropTypes.func,
    interval: PropTypes.number
};

export default connect(
    state => ({
        config: state.config,
        reloadHash: state.reloadHash
    }),
    dispatch => ({dispatch})
)(Reloader);
 