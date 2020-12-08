import {createAction} from 'redux-actions';

import {IsLoadingActionType, IsLoadingState} from '../reducers/isLoading';

export const setIsLoading = createAction<IsLoadingState>(
    IsLoadingActionType.Set
);
