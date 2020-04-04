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
        const {error, paths, layout, dependenciesRequest} = this.props;
        return (
            <div id="_dash-global-error-container">
                <DebugMenu
                    error={error}
                    paths={paths}
                    layout={layout}
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
    dependenciesRequest: PropTypes.object,
};

const GlobalErrorContainer = connect(state => ({
    error: state.error,
    paths: state.paths,
    layout: state.layout,
    dependenciesRequest: state.dependenciesRequest,
}))(Radium(UnconnectedGlobalErrorContainer));

export default GlobalErrorContainer;
