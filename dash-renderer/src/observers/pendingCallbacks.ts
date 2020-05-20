import {
    equals,
    flatten,
    forEach,
    isEmpty,
    map,
    reduce
} from 'ramda';

import { setPendingCallbacks } from '../actions/callbacks';
import { setLoadingMap } from '../actions/loadingMap';
import { getPendingCallbacks } from '../utils/callbacks';
import { IStoreObserverDefinition } from '../StoreObserver';
import { IStoreState } from '../store';

const observer: IStoreObserverDefinition<IStoreState> = {
    observer: ({
        dispatch,
        getState
    }) => {
        const {
            callbacks,
            callbacks: {
                executing,
                watched,
                executed
            },
            loadingMap,
            paths,
            pendingCallbacks
        } = getState();

        console.log('onCallbacksChanged.pendingCallbacks', callbacks);

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
            console.log('SPECIAL', '[setLoadingMap]', nextMap);
            dispatch(setLoadingMap(nextMap));
        }

        /*
         * If the calculated list of pending callbacks is not
         * equivalent to the current one, update it.
         */
        const next = getPendingCallbacks(callbacks);
        if (
            !pendingCallbacks ||
            pendingCallbacks.length !== next.length ||
            !next.every((v, i) =>
                v === pendingCallbacks[i] ||
                v.callback === pendingCallbacks[i].callback)
        ) {
            console.log('SPECIAL', '[setPendingCallbacks]', next);
            dispatch(setPendingCallbacks(next));
        }
    },
    inputs: ['callbacks']
};

export default observer;