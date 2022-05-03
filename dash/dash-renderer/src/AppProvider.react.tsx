import PropTypes from 'prop-types';
import React from 'react';
import {Provider} from 'react-redux';

import store from './store';
import AppContainer from './AppContainer.react';

const AppProvider = ({hooks}: any) => {
    return (
        <Provider store={store.store}>
            <AppContainer hooks={hooks} />
        </Provider>
    );
};

AppProvider.propTypes = {
    hooks: PropTypes.shape({
        request_pre: PropTypes.func,
        request_post: PropTypes.func,
        callback_resolved: PropTypes.func,
        request_refresh_jwt: PropTypes.func
    })
};

AppProvider.defaultProps = {
    hooks: {
        request_pre: null,
        request_post: null,
        callback_resolved: null,
        request_refresh_jwt: null
    }
};

export default AppProvider;
