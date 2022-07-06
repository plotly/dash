import {once} from 'ramda';
import {createStore, applyMiddleware, Store, Observer} from 'redux';
import thunk from 'redux-thunk';
import {createReducer} from './reducers/reducer';
import StoreObserver from './StoreObserver';
import {ICallbacksState} from './reducers/callbacks';
import {LoadingMapState} from './reducers/loadingMap';
import {IsLoadingState} from './reducers/isLoading';

import documentTitle from './observers/documentTitle';
import executedCallbacks from './observers/executedCallbacks';
import executingCallbacks from './observers/executingCallbacks';
import isLoading from './observers/isLoading';
import loadingMap from './observers/loadingMap';
import prioritizedCallbacks from './observers/prioritizedCallbacks';
import requestedCallbacks from './observers/requestedCallbacks';
import storedCallbacks from './observers/storedCallbacks';

export interface IStoreState {
    callbacks: ICallbacksState;
    isLoading: IsLoadingState;
    loadingMap: LoadingMapState;
    [key: string]: any;
}

export interface IStoreObserver {
    observer: Observer<Store<IStoreState>>;
    inputs: string[];
}

export default class RendererStore {
    constructor() {
        this.__store = this.initializeStore();
    }

    private __store: Store<IStoreState>;
    public get store(): Store<IStoreState> {
        return this.__store;
    }

    private readonly storeObserver = new StoreObserver<IStoreState>();

    private setObservers = once(() => {
        const observe = this.storeObserver.observe;

        observe(documentTitle);
        observe(isLoading);
        observe(loadingMap);
        observe(requestedCallbacks);
        observe(prioritizedCallbacks);
        observe(executingCallbacks);
        observe(executedCallbacks);
        observe(storedCallbacks);
    });

    private createAppStore = (reducer: any, middleware: any) => {
        this.__store = createStore(reducer, middleware);
        this.storeObserver.setStore(this.__store);
        this.setObservers();
    };

    /**
     * Initialize a Redux store with thunk, plus logging (only in development mode) middleware
     *
     * @param {bool} reset: discard any previous store
     *
     * @returns {Store<GenericStoreEnhancer>}
     *  An initialized redux store with middleware and possible hot reloading of reducers
     */
    initializeStore = (reset?: boolean): Store<IStoreState> => {
        if (this.__store && !reset) {
            return this.__store;
        }

        const reducer = createReducer();

        // eslint-disable-next-line no-process-env
        if (process.env.NODE_ENV === 'production') {
            this.createAppStore(reducer, applyMiddleware(thunk));
        } else {
            // only attach logger to middleware in non-production mode
            const reduxDTEC = (window as any)
                .__REDUX_DEVTOOLS_EXTENSION_COMPOSE__;
            if (reduxDTEC) {
                this.createAppStore(
                    reducer,
                    reduxDTEC({actionsDenylist: ['reloadRequest']})(
                        applyMiddleware(thunk)
                    )
                );
            } else {
                this.createAppStore(reducer, applyMiddleware(thunk));
            }
        }

        if (!reset) {
            // TODO - Protect this under a debug mode?
            (window as any).store = this.__store;
        }

        if ((module as any).hot) {
            // Enable hot module replacement for reducers
            (module as any).hot.accept('./reducers/reducer', () => {
                const nextRootReducer =
                    require('./reducers/reducer').createReducer();

                this.__store.replaceReducer(nextRootReducer);
            });
        }

        return this.__store;
    };
}
