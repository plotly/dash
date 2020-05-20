import PropTypes from 'prop-types';
import React from 'react';
import {Provider} from 'react-redux';

import initializeStore, { observe } from './store';
import AppContainer from './AppContainer.react';

import loadingMap from './observers/loadingMap';
import requestedCallbacks from './observers/requestedCallbacks';
import prioritizeCallbacks from './observers/prioritizedCallbacks';
import executingCallbacks from './observers/executingCallbacks';
import executedCallbacks from './observers/executedCallbacks';
import storedCallbacks from './observers/storedCallbacks';

const store = initializeStore();
observe(loadingMap);
observe(requestedCallbacks);
observe(prioritizeCallbacks);
observe(executingCallbacks);
observe(executedCallbacks);
observe(storedCallbacks);

const AppProvider = ({hooks}: any) => {
    return (
        <Provider store={store}>
            <AppContainer hooks={hooks} />
        </Provider>
    );
};

AppProvider.propTypes = {
    hooks: PropTypes.shape({
        request_pre: PropTypes.func,
        request_post: PropTypes.func,
    }),
};

AppProvider.defaultProps = {
    hooks: {
        request_pre: null,
        request_post: null,
    },
};

export default AppProvider;


