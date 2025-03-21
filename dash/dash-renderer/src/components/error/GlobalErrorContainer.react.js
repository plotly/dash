import {connect} from 'react-redux';
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {DebugMenu} from './menu/DebugMenu.react';

class UnconnectedGlobalErrorContainer extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        const {config, error, children} = this.props;
        return (
            <div
                id='_dash-global-error-container'
                style={{
                    position: 'absolute',
                    maxHeight: '100vh',
                    height: '100vh',
                    maxWidth: '100vw',
                    width: '100vw'
                }}
                className='display-dash-debug'
            >
                <div id='_dash-app-content'>{children}</div>
                <DebugMenu
                    config={config}
                    error={error}
                    hotReload={Boolean(config.hot_reload)}
                />
            </div>
        );
    }
}

UnconnectedGlobalErrorContainer.propTypes = {
    children: PropTypes.object,
    config: PropTypes.object,
    error: PropTypes.object
};

const GlobalErrorContainer = connect(state => ({
    config: state.config,
    error: state.error
}))(UnconnectedGlobalErrorContainer);

export default GlobalErrorContainer;
