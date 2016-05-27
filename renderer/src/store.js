/* global module, require */

import {createStore} from 'redux'

import reducer from './reducers/reducer';

let store;
export const initializeStore = () => {
    if (store) {
        return store;
    }

    store = createStore(reducer);

    if (module.hot) {
        // Enable hot module replacement for reducers
        module.hot.accept('./reducers/reducer', () => {
          const nextRootReducer = require('./reducers/reducer');
          store.replaceReducer(nextRootReducer);
        });
    }

    return store;
};

