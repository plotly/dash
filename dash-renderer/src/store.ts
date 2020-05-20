import { createStore, applyMiddleware, Store, Observer } from 'redux';
import thunk from 'redux-thunk';
import {createReducer} from './reducers/reducer';
import StoreObserver from './StoreObserver';
import { ICallbacksState } from './reducers/callbacks';
import { LoadingMapState } from './reducers/loadingMap';

export interface IStoreState {
    callbacks: ICallbacksState;
    loadingMap: LoadingMapState;
    [key: string]: any;
}

let store: Store<IStoreState>;
const storeObserver = new StoreObserver<IStoreState>();

export const observe = storeObserver.observe;

export interface IStoreObserver {
    observer: Observer<Store<IStoreState>>;
    inputs: string[];
}

function createAppStore(reducer: any, middleware: any) {
    store = createStore(reducer, middleware);
    storeObserver.setStore(store);
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
