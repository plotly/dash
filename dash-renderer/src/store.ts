import { once } from 'ramda';
import { createStore, applyMiddleware, Store, Observer } from 'redux';
import thunk from 'redux-thunk';
import {createReducer} from './reducers/reducer';
import StoreObserver from './StoreObserver';
import { ICallbacksState } from './reducers/callbacks';
import { LoadingMapState } from './reducers/loadingMap';
import { IsLoadingState } from './reducers/isLoading';

import documentTitle from './observers/documentTitle';
import executedCallbacks from './observers/executedCallbacks';
import executingCallbacks from './observers/executingCallbacks';
import isLoading from './observers/isLoading'
import loadingMap from './observers/loadingMap';
import prioritizedCallbacks from './observers/prioritizedCallbacks';
import requestedCallbacks from './observers/requestedCallbacks';
import storedCallbacks from './observers/storedCallbacks';

export interface IStoreObserver {
    observer: Observer<Store<IStoreState>>;
    inputs: string[];
}

export interface IStoreState {
    callbacks: ICallbacksState;
    isLoading: IsLoadingState;
    loadingMap: LoadingMapState;
    [key: string]: any;
}

let store: Store<IStoreState>;
const storeObserver = new StoreObserver<IStoreState>();

const setObservers = once(() => {
    const observe = storeObserver.observe;

    observe(documentTitle);
    observe(isLoading);
    observe(loadingMap);
    observe(requestedCallbacks);
    observe(prioritizedCallbacks);
    observe(executingCallbacks);
    observe(executedCallbacks);
    observe(storedCallbacks);
});

function createAppStore(reducer: any, middleware: any) {
    store = createStore(reducer, middleware);
    storeObserver.setStore(store);
    setObservers();
}

/**
 * Initialize a Redux store with thunk, plus logging (only in development mode) middleware
 *
 * @param {bool} reset: discard any previous store
 *
 * @returns {Store<GenericStoreEnhancer>}
 *  An initialized redux store with middleware and possible hot reloading of reducers
 */
const initializeStore = (reset?: boolean): Store<IStoreState> => {
    if (store && !reset) {
        return store;
    }

    const reducer = createReducer();

    // eslint-disable-next-line no-process-env
    if (process.env.NODE_ENV === 'production') {
        createAppStore(reducer, applyMiddleware(thunk));
    } else {
        // only attach logger to middleware in non-production mode
        const reduxDTEC = (window as any).__REDUX_DEVTOOLS_EXTENSION_COMPOSE__;
        if (reduxDTEC) {
            createAppStore(reducer, reduxDTEC(applyMiddleware(thunk)));
        } else {
            createAppStore(reducer, applyMiddleware(thunk));
        }
    }

    if (!reset) {
        // TODO - Protect this under a debug mode?
        (window as any).store = store;
    }

    if ((module as any).hot) {
        // Enable hot module replacement for reducers
        (module as any).hot.accept('./reducers/reducer', () => {
            const nextRootReducer = require('./reducers/reducer').createReducer();

            store.replaceReducer(nextRootReducer);
        });
    }

    return store;
};

export default initializeStore;
