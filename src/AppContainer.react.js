import {connect} from 'react-redux';
import React from 'react';
import Authentication from './Authentication.react';
import APIController from './APIController.react';
import DocumentTitle from './components/core/DocumentTitle.react';
import Loading from './components/core/Loading.react';
import Toolbar from './components/core/Toolbar.react';

function UnconnectedAppContainer() {
    return (
        <Authentication>
            <div>
                <Toolbar/>
                <APIController/>
                <DocumentTitle/>
                <Loading/>
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
