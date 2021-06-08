import {IStoreObserverDefinition} from '../StoreObserver';
import {IStoreState} from '../store';

const updateTitle = (getState: () => IStoreState) => {
    const {config, isLoading} = getState();

    const update_title = config?.update_title;

    if (!update_title) {
        return;
    }

    if (isLoading) {
        if (document.title !== update_title) {
            observer.title = document.title;
            document.title = update_title;
        }
    } else {
        if (document.title === update_title) {
            document.title = observer.title;
        } else {
            observer.title = document.title;
        }
    }
};

const observer: IStoreObserverDefinition<IStoreState> = {
    inputs: ['isLoading'],
    mutationObserver: undefined,
    observer: ({getState}) => {
        const {config} = getState();

        if (observer.config !== config) {
            observer.config = config;
            observer.mutationObserver?.disconnect();
            observer.mutationObserver = new MutationObserver(() =>
                updateTitle(getState)
            );

            const title = document.querySelector('title');
            if (title) {
                observer.mutationObserver.observe(title, {
                    subtree: true,
                    childList: true,
                    attributes: true,
                    characterData: true
                });
            }
        }

        updateTitle(getState);
    }
};

export default observer;
