import {createStore, applyMiddleware} from 'redux';
import thunk from 'redux-thunk';
import {createReducer} from './reducers/reducer';

let store;

/**
 * Initialize a Redux store with thunk, plus logging (only in development mode) middleware
 *
 * @param {bool} reset: discard any previous store
 *
 * @returns {Store<GenericStoreEnhancer>}
 *  An initialized redux store with middleware and possible hot reloading of reducers
 */
const initializeStore = reset => {
    if (store && !reset) {
        return store;
    }

    const reducer = createReducer();

    // only attach logger to middleware in non-production mode
    store =
        process.env.NODE_ENV === 'production' // eslint-disable-line no-process-env
            ? createStore(reducer, applyMiddleware(thunk))
            : createStore(
                  reducer,
                  window.__REDUX_DEVTOOLS_EXTENSION__ &&
                      window.__REDUX_DEVTOOLS_EXTENSION__(),
                  applyMiddleware(thunk)
              );

    if (!reset) {
        // TODO - Protect this under a debug mode?
        window.store = store;
    }

    if (module.hot) {
        // Enable hot module replacement for reducers
        module.hot.accept('./reducers/reducer', () => {
            const nextRootReducer = require('./reducers/reducer').createReducer();

            store.replaceReducer(nextRootReducer);
        });
    }

    return store;
};

export default initializeStore;
