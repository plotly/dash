/* global module, require */

import {createStore, applyMiddleware} from 'redux';
import thunk from 'redux-thunk';
import reducer from './reducers/reducer';
import createLogger from 'redux-logger';


let logger;
// only set up logger in non-production mode
if (process.env.NODE_ENV !== 'production')
    {logger = createLogger();}
let store;

/**
 * Initialize a Redux store with thunk, plus logging (only in development mode) middleware
 *
 * @returns {Store<GenericStoreEnhancer>}
 *  An initialized redux store with middleware and possible hot reloading of reducers
 */
const initializeStore = () => {
    if (store) {
        return store;
    }

    // only attach logger to middleware in non-production mode
    store = process.env.NODE_ENV === 'production'
        ? createStore(reducer, applyMiddleware(thunk))
        : createStore(reducer, applyMiddleware(thunk, logger));


    // TODO - Protect this under a debug mode?
    window.store = store; /* global window:true */

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
