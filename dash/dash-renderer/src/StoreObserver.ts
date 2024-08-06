import {any, filter, map, path} from 'ramda';

import {Store, Unsubscribe} from 'redux';

type Observer<TStore> = (store: TStore) => void;
type UnregisterObserver = () => void;

interface IStoreObserverState<TStore> {
    inputPaths: string[][];
    lastState: any;
    observer: Observer<TStore>;
    triggered: boolean;
}

export interface IStoreObserverDefinition<TStore> {
    observer: Observer<Store<TStore>>;
    inputs: string[];
    [key: string]: any;
}

export default class StoreObserver<TStore> {
    private _store?: Store<TStore>;
    private _unsubscribe?: Unsubscribe;

    private readonly _observers: IStoreObserverState<Store<TStore>>[] = [];

    constructor(store?: Store<TStore>) {
        this.__init__(store);
    }

    observe = (
        observer: IStoreObserverDefinition<TStore> | Observer<Store<TStore>>,
        inputs?: string[]
    ): UnregisterObserver => {
        if (typeof observer === 'function') {
            if (!Array.isArray(inputs)) {
                throw new Error('inputs must be an array');
            }

            this.add(observer, inputs);
            return () => this.remove(observer);
        }

        this.add(observer.observer, observer.inputs);
        return () => this.remove(observer.observer);
    };

    setStore = (store: Store<TStore>) => {
        this.__finalize__();
        this.__init__(store);
    };

    private __finalize__ = () => this._unsubscribe?.();

    private __init__ = (store?: Store<TStore>) => {
        this._store = store;
        if (store) {
            this._unsubscribe = store.subscribe(this.notify);
        }

        this._observers.forEach(o => {
            o.lastState = null;
        });
    };

    private add = (observer: Observer<Store<TStore>>, inputs: string[]) =>
        this._observers.push({
            inputPaths: map(p => p.split('.'), inputs),
            lastState: null,
            observer,
            triggered: false
        });

    private notify = () => {
        const store = this._store;
        if (!store) {
            return;
        }

        const state = store.getState();

        const triggered = filter(
            o =>
                !o.triggered &&
                any(i => path(i, state) !== path(i, o.lastState), o.inputPaths),
            this._observers
        );

        triggered.forEach(o => {
            o.triggered = true;
        });

        triggered.forEach(o => {
            o.lastState = store.getState();
            o.observer(store);
            o.triggered = false;
        });
    };

    private remove = (observer: Observer<Store<TStore>>) =>
        this._observers.splice(
            this._observers.findIndex(
                o => observer === o.observer,
                this._observers
            ),
            1
        );
}
