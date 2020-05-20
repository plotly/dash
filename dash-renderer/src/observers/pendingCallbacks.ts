import { setPendingCallbacks } from '../actions/callbacks';
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
            pendingCallbacks
        } = getState();

        const next = getPendingCallbacks(callbacks);

        /**
         * If the calculated list of pending callbacks is equivalent
         * to the previous one, do not update it.
         */
        if (
            pendingCallbacks &&
            pendingCallbacks.length === next.length &&
            next.every((v, i) =>
                v === pendingCallbacks[i] ||
                v.callback === pendingCallbacks[i].callback)
        ) {
            return;
        }

        dispatch(setPendingCallbacks(next));
    }, inputs: ['callbacks']
};

export default observer;