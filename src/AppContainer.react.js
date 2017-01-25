import React from 'react';
import {Provider} from 'react-redux'

import initializeStore from './store';
import TreeContainer from './TreeContainer.react';
import { initialize } from './actions';

const store = initializeStore();
// Initialization
store.dispatch(initialize());

export default () => (
    <Provider store={store}>
        <TreeContainer/>
    </Provider>
);
