import {connect} from 'react-redux';
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import Radium from 'radium';
import {DebugMenu} from './menu/DebugMenu.react';

class UnconnectedGlobalErrorContainer extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        const {error, paths, layout, changed, profile, dependenciesRequest} = this.props;
        return (
            <div id="_dash-global-error-container">
                <DebugMenu
                    error={error}
                    paths={paths}
                    layout={layout}
                    changed={changed}
                    profile={profile}
                    dependenciesRequest={dependenciesRequest}
                >
                    <div id="_dash-app-content">{this.props.children}</div>
                </DebugMenu>
            </div>
        );
    }
}

UnconnectedGlobalErrorContainer.propTypes = {
    children: PropTypes.object,
    error: PropTypes.object,
    paths: PropTypes.object,
    layout: PropTypes.object,
    history: PropTypes.object,
    profile: PropTypes.object,
    dependenciesRequest: PropTypes.object,
};

const GlobalErrorContainer = connect(state => ({
    error: state.error,
    paths: state.paths,
    layout: state.layout,
    changed: state.changed,
    profile: state.profile,
    dependenciesRequest: state.dependenciesRequest,
}))(Radium(UnconnectedGlobalErrorContainer));

export default GlobalErrorContainer;
