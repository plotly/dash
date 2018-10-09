import React from 'react';
import {Provider} from 'react-redux';

import initializeStore from './store';
import AppContainer from './AppContainer.react';

const store = initializeStore();

const AppProvider = () => (
    <Provider store={store}>
        <AppContainer />
    </Provider>
);

export default AppProvider;
