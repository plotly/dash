import {connect} from 'react-redux';
import React from 'react';
import PropTypes from 'prop-types';
import APIController from './APIController.react';
import DocumentTitle from './components/core/DocumentTitle.react';
import Loading from './components/core/Loading.react';
import Toolbar from './components/core/Toolbar.react';
import Reloader from './components/core/Reloader.react';
import {readConfig} from './actions';

class UnconnectedAppContainer extends React.Component {

    componentWillMount() {
        const {dispatch} = this.props;
        dispatch(readConfig())
    }

    render() {
        return (
            <div>
                <Toolbar />
                <APIController />
                <DocumentTitle />
                <Loading />
                <Reloader />
            </div>
        );
    }
}

UnconnectedAppContainer.propTypes = {
    dispatch: PropTypes.func,
};

const AppContainer = connect(
    state => ({
        history: state.history,
    }),
    dispatch => ({dispatch})
)(UnconnectedAppContainer);

export default AppContainer;
