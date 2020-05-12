import {
    any,
    forEach,
    map,
    path
} from 'ramda';

import { Store, Unsubscribe } from 'redux';

type Observer<TStore> = (store: TStore) => void;
type UnregisterObserver = () => void;

interface IStoreObserver<TStore> {
    inputPaths: string[][];
    lastState: any;
    observer: Observer<TStore>;
    triggered: boolean;
}

export default class StoreObserver<TStore extends Store> {
    private _store?: TStore;
    private _unsubscribe?: Unsubscribe;

    private readonly _observers: IStoreObserver<TStore>[] = [];

    constructor(store?: TStore) {
        this.__init__(store);
    }

    observe = (
        observer: Observer<TStore>,
        inputs: string[]
    ): UnregisterObserver => {
        this.add(observer, inputs);

        return () => this.remove(observer);
    }

    setStore = (store: TStore) => {
        this.__finalize__();
        this.__init__(store);
    }

    private __finalize__ = () => this._unsubscribe?.()

    private __init__ = (store?: TStore) => {
        this._store = store;
        if (store) {
            this._unsubscribe = store.subscribe(this.notify);
        }

        forEach(o => o.lastState = null, this._observers);
    }

    private add = (
        observer: Observer<TStore>,
        inputs: string[]
    ) => this._observers.push({
        inputPaths: map(p => p.split('.'), inputs),
        lastState: null,
        observer,
        triggered: false
    });

    private notify = () => forEach(
        this.notifyObserver,
        this._observers
    );

    private notifyObserver = (o: IStoreObserver<TStore>) => {
        const store = this._store;
        if (!store) {
            return;
        }

        const state: any = store.getState();

        /** Don't trigger if nested */
        if (o.triggered) {
            return;
        }

        const { inputPaths, lastState, observer } = o;

        /** Don't notify observer if there's no change */
        if (!any(
            i => path(i, state) !== path(i, lastState),
            inputPaths
        )) {
            return;
        }

        o.triggered = true;
        /**
         * Due to nested store updates, the state could change between the
         * observer call and setting `lastState`, leading to untriggered changes
         */
        const s = store.getState();
        observer(store);

        o.triggered = false;
        o.lastState = s;
    };

    private remove = (observer: Observer<TStore>) => this._observers.splice(
        this._observers.findIndex(
            o => observer === o.observer,
            this._observers
        ), 1
    );
}