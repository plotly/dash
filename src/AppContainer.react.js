import {connect} from 'react-redux';
import React from 'react';
import Authentication from './Authentication.react';
import APIController from './APIController.react';
import DocumentTitle from './components/core/DocumentTitle.react';
import Toolbar from './components/core/Toolbar.react';

function UnconnectedAppContainer() {
    return (
        <Authentication>
            <div>
                <Toolbar/>
                <APIController/>
                <DocumentTitle/>
            </div>
        </Authentication>
    );
}

const AppContainer = connect(
    state => ({
        history: state.history
    }),
    dispatch => ({dispatch})
)(UnconnectedAppContainer);

export default AppContainer;
