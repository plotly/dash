import {IStoreObserverDefinition} from '../StoreObserver';
import {IStoreState} from '../store';
import {getPendingCallbacks} from '../utils/callbacks';
import {setIsLoading} from '../actions/isLoading';

const observer: IStoreObserverDefinition<IStoreState> = {
    observer: ({dispatch, getState}) => {
        const {callbacks, isLoading} = getState();

        const pendingCallbacks = getPendingCallbacks(callbacks);

        // Filter out persistent callbacks - they shouldn't trigger the loading indicator
        const nonPersistentCallbacks = pendingCallbacks.filter(
            cb => !cb.callback.persistent
        );

        const next = Boolean(nonPersistentCallbacks.length);

        if (isLoading !== next) {
            dispatch(setIsLoading(next));
        }
    },
    inputs: ['callbacks']
};

export default observer;
