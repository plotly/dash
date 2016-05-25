/* global module, require */

import {createStore} from 'redux'

import reducer from './reducers/reducer';

export const initializeStore = () => {
    const store = createStore(reducer);

    if (module.hot) {
        // Enable hot module replacement for reducers
        module.hot.accept('./reducers', () => {
          const nextRootReducer = require('./reducers/reducer');
          store.replaceReducer(nextRootReducer);
        });
    }

    return store;
};

