import {createAction} from 'redux-actions';

import {LoadingMapActionType, LoadingMapState} from '../reducers/loadingMap';

export const setLoadingMap = createAction<LoadingMapState>(
    LoadingMapActionType.Set
);
