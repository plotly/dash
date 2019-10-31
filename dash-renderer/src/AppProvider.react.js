import React from 'react';
import {Provider} from 'react-redux';

import initializeStore from './store';
import AppContainer from './AppContainer.react';

import PropTypes from 'prop-types';

const store = initializeStore();

const AppProvider = ({hooks}) => {
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
        csrf_config: PropTypes.object,
    }),
};

AppProvider.defaultProps = {
    hooks: {
        request_pre: null,
        request_post: null,
        csrf_config: null,
    },
};

export default AppProvider;
