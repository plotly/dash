import {
    equals,
    flatten,
    forEach,
    isEmpty,
    map,
    reduce
} from 'ramda';

import { setLoadingMap } from '../actions/loadingMap';
import { IStoreObserverDefinition } from '../StoreObserver';
import { IStoreState } from '../store';

const observer: IStoreObserverDefinition<IStoreState> = {
    observer: ({
        dispatch,
        getState
    }) => {
        const {
            callbacks: {
                executing,
                watched,
                executed
            },
            loadingMap,
            paths
        } = getState();

        const callbacks = [...executing, ...watched, ...executed];
        console.log('onCallbacksChanged.loadingMap', callbacks);

        /*
            Get the path of all components impacted by callbacks
            with states: executing, watched, executed
        */

        const loadingPaths = flatten(map(
            cb => cb.getOutputs(paths),
            [...executing, ...watched, ...executed]
        ));

        const nextMap: any = isEmpty(loadingPaths) ?
            null :
            reduce(
                (res, path) => {
                    let target = res;
                    target.__dashprivate__idprop__ = target.__dashprivate__idprop__ || [];
                    target.__dashprivate__idprop__.push({
                        id: path.id,
                        property: path.property
                    });

                    forEach(p => {
                        target = (target[p] =
                            target[p] ??
                                p === 'children' ? [] : {}
                        )

                        target.__dashprivate__idprop__ = target.__dashprivate__idprop__ || [];
                        target.__dashprivate__idprop__.push({
                            id: path.id,
                            property: path.property
                        });

                    }, path.path);

                    return res;
                },
                {} as any,
                loadingPaths
            );

        if (!equals(nextMap, loadingMap)) {
            dispatch(setLoadingMap(nextMap));
        }
    },
    inputs: ['callbacks.executing', 'callbacks.watched', 'callbacks.executed']
};

export default observer;