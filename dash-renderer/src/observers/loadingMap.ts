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

        /*
            Get the path of all components impacted by callbacks
            with states: executing, watched, executed.

            For each path, keep track of all (id,prop) tuples that
            are impacted for this node and nested nodes.
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
                    const idprop = {
                        id: path.id,
                        property: path.property
                    };

                    // Assign one affected prop for this path
                    target.__dashprivate__idprop__ = target.__dashprivate__idprop__ || idprop;
                    // Assign all affected props for this path and nested paths
                    target.__dashprivate__idprops__ = target.__dashprivate__idprops__ || [];
                    target.__dashprivate__idprops__.push(idprop);

                    forEach(p => {
                        target = (target[p] =
                            target[p] ??
                                p === 'children' ? [] : {}
                        )

                        target.__dashprivate__idprops__ = target.__dashprivate__idprops__ || [];
                        target.__dashprivate__idprops__.push(idprop);
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