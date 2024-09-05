import PropTypes from 'prop-types';
import React, {useState} from 'react';
import {Provider} from 'react-redux';

import Store from './store';
import AppContainer from './AppContainer.react';

const AppProvider = ({hooks}: any) => {
    const [{store}] = useState(() => new Store());
    return (
        <Provider store={store}>
            <AppContainer hooks={hooks} />
        </Provider>
    );
};

AppProvider.propTypes = {
    hooks: PropTypes.shape({
        layout_pre: PropTypes.func,
        layout_post: PropTypes.func,
        request_pre: PropTypes.func,
        request_post: PropTypes.func,
        callback_resolved: PropTypes.func,
        request_refresh_jwt: PropTypes.func
    })
};

AppProvider.defaultProps = {
    hooks: {
        layout_pre: null,
        layout_post: null,
        request_pre: null,
        request_post: null,
        callback_resolved: null,
        request_refresh_jwt: null
    }
};

export default AppProvider;
