import PropTypes from 'prop-types';
import React, {useState, useEffect} from 'react';
import {Provider} from 'react-redux';

import Store from './store';
import AppContainer from './AppContainer.react';
import getConfigFromDOM from './config';
import {
    initializeWebSocket,
    disconnectWebSocket
} from './observers/websocketObserver';

const AppProvider = ({
    hooks = {
        layout_pre: null,
        layout_post: null,
        request_pre: null,
        request_post: null,
        callback_resolved: null,
        request_refresh_jwt: null
    }
}: any) => {
    const [{store}] = useState(() => new Store());

    // Initialize WebSocket connection if enabled or if websocket config is available
    // (for per-callback websocket=True)
    useEffect(() => {
        const config = getConfigFromDOM();
        if (
            config.websocket?.enabled ||
            (config.websocket?.url && config.websocket?.worker_url)
        ) {
            // Add fetch config for consistency
            const fullConfig = {
                ...config,
                fetch: {
                    credentials: 'same-origin',
                    headers: {
                        Accept: 'application/json',
                        'Content-Type': 'application/json'
                    }
                }
            };
            initializeWebSocket(store, fullConfig);
        }

        // Cleanup on unmount
        return () => {
            disconnectWebSocket();
        };
    }, [store]);

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

export default AppProvider;
