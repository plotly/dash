import {connect} from 'react-redux';
import React from 'react';
import APIController from './APIController.react';
import Loading from './components/core/Loading.react';
import Toolbar from './components/core/Toolbar.react';

function UnconnectedAppContainer() {
    return (
        <div>
            <Toolbar/>
            <Loading/>
        </div>
                <APIController/>
    );
}

const AppContainer = connect(
    state => ({
        history: state.history
    }),
    dispatch => ({dispatch})
)(UnconnectedAppContainer);

export default AppContainer;
