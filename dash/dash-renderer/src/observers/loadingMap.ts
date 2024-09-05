import {equals, flatten, isEmpty, map, reduce} from 'ramda';

import {setLoadingMap} from '../actions/loadingMap';
import {IStoreObserverDefinition} from '../StoreObserver';
import {IStoreState} from '../store';
import {ILayoutCallbackProperty} from '../types/callbacks';

const observer: IStoreObserverDefinition<IStoreState> = {
    observer: ({dispatch, getState}) => {
        const {
            callbacks: {executing, watched, executed},
            loadingMap,
            paths
        } = getState();

        /*
            Get the path of all components impacted by callbacks
            with states: executing, watched, executed.

            For each path, keep track of all (id,prop) tuples that
            are impacted for this node and nested nodes.
        */

        const loadingPaths: ILayoutCallbackProperty[] = flatten(
            map(
                cb => cb.getOutputs(paths),
                [...executing, ...watched, ...executed]
            )
        );

        const nextMap: any = isEmpty(loadingPaths)
            ? null
            : reduce(
                  (res, {id, property, path}) => {
                      let target = res;
                      const idprop = {id, property};

                      // Assign all affected props for this path and nested paths
                      target.__dashprivate__idprops__ =
                          target.__dashprivate__idprops__ || [];
                      target.__dashprivate__idprops__.push(idprop);

                      path.forEach((p, i) => {
                          target = target[p] =
                              target[p] ??
                              (p === 'children' &&
                              typeof path[i + 1] === 'number'
                                  ? []
                                  : {});

                          target.__dashprivate__idprops__ =
                              target.__dashprivate__idprops__ || [];
                          target.__dashprivate__idprops__.push(idprop);
                      });

                      // Assign one affected prop for this path
                      target.__dashprivate__idprop__ =
                          target.__dashprivate__idprop__ || idprop;

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
