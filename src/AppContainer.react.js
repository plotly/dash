import React from 'react';
import {Provider} from 'react-redux'

import initializeStore from './store';
import TreeContainer from './TreeContainer.react';
import Loading from './components/core/Loading.react';
import { initialize } from './actions';

const store = initializeStore();
// Initialization
store.dispatch(initialize());

const AppContainer = () => (
    <Provider store={store}>
        <div>
            <TreeContainer/>
            <Loading/>
        </div>
    </Provider>
);

export default AppContainer;
