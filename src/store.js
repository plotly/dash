/* global module, require */

import {createStore, applyMiddleware} from 'redux';
import thunk from 'redux-thunk';
import reducer from './reducers/reducer';
import createLogger from 'redux-logger';

const logger = createLogger()
let store;
const initializeStore = () => {
    if (store) {
        return store;
    }

    store = createStore(
        reducer,
        // TODO - Remove logger from production
        applyMiddleware(thunk, logger)
    );

    if (module.hot) {
        // Enable hot module replacement for reducers
        module.hot.accept('./reducers/reducer', () => {
            const nextRootReducer = require('./reducers/reducer');

            store.replaceReducer(nextRootReducer);
        });
    }

    return store;
};

export default initializeStore;
