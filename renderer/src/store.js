import { createStore, applyMiddleware } from 'redux'
import thunk from 'redux-thunk'

import reducer from './reducers/reducer';

export const initializeStore = () => {
    const store = createStore(
        reducer,
        applyMiddleware(thunk)
    );

    if (module.hot) {
        // Enable hot module replacement for reducers
        module.hot.accept('./reducers', () => {
          const nextRootReducer = require('./reducers/reducer');
          store.replaceReducer(nextRootReducer);
        });
    }

    return store;
};

