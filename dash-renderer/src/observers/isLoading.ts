import {IStoreObserverDefinition} from '../StoreObserver';
import {IStoreState} from '../store';
import {getPendingCallbacks} from '../utils/callbacks';
import {setIsLoading} from '../actions/isLoading';

const observer: IStoreObserverDefinition<IStoreState> = {
    observer: ({dispatch, getState}) => {
        const {callbacks, isLoading} = getState();

        const pendingCallbacks = getPendingCallbacks(callbacks);

        const next = Boolean(pendingCallbacks.length);

        if (isLoading !== next) {
            dispatch(setIsLoading(next));
        }
    },
    inputs: ['callbacks']
};

export default observer;
