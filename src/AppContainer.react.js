import React from 'react';
import {Provider} from 'react-redux'

import initializeStore from './store';
import TreeContainer from './TreeContainer.react';
import Loading from './components/core/Loading.react';

const store = initializeStore();

const AppContainer = () => (
    <Provider store={store}>
        <div>
            <TreeContainer/>
            <Loading/>
        </div>
    </Provider>
);

export default AppContainer;
