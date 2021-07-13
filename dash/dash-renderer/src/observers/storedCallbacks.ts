import {
    concat,
    filter,
    groupBy,
    isNil,
    partition,
    reduce,
    toPairs
} from 'ramda';

import {IStoreState} from '../store';

import {aggregateCallbacks, removeStoredCallbacks} from '../actions/callbacks';

import {ICallback, IStoredCallback} from '../types/callbacks';

import {getPendingCallbacks} from '../utils/callbacks';
import {IStoreObserverDefinition} from '../StoreObserver';

const observer: IStoreObserverDefinition<IStoreState> = {
    observer: ({dispatch, getState}) => {
        const {callbacks} = getState();
        const pendingCallbacks = getPendingCallbacks(callbacks);

        const {
            callbacks: {stored}
        } = getState();

        const [nullGroupCallbacks, groupCallbacks] = partition(
            cb => isNil(cb.executionGroup),
            stored
        );

        const executionGroups = groupBy<IStoredCallback>(
            cb => cb.executionGroup as any,
            groupCallbacks
        );

        const pendingGroups = groupBy<ICallback>(
            cb => cb.executionGroup as any,
            filter(cb => !isNil(cb.executionGroup), pendingCallbacks)
        );

        const dropped = reduce(
            (res, [executionGroup, executionGroupCallbacks]) =>
                !pendingGroups[executionGroup]
                    ? concat(res, executionGroupCallbacks)
                    : res,
            [] as IStoredCallback[],
            toPairs(executionGroups)
        );

        dispatch(
            aggregateCallbacks([
                nullGroupCallbacks.length
                    ? removeStoredCallbacks(nullGroupCallbacks)
                    : null,
                dropped.length ? removeStoredCallbacks(dropped) : null
            ])
        );
    },
    inputs: ['callbacks.stored', 'callbacks.completed']
};

export default observer;
