import {LibrariesActions} from '../libraries/libraryTypes';

const createAction = (type: LibrariesActions) => (payload: any) => ({
    type,
    payload
});

export const setLibraryLoading = createAction(LibrariesActions.LOAD);
export const setLibraryLoaded = createAction(LibrariesActions.LOADED);
export const setLibraryToLoad = createAction(LibrariesActions.TO_LOAD);
