import {assocPath, pipe} from 'ramda';
import {LibrariesActions, LibrariesState} from '../libraries/libraryTypes';

type LoadingPayload = {
    libraries: string[];
};

type LoadedPayload = {
    libraries: string[];
};

type ToLoadPayload = {
    library: string;
};

type LibrariesAction = {
    type: LibrariesActions;
    payload: LoadingPayload | LoadedPayload | ToLoadPayload;
};

function handleLoad(library: string, state: LibrariesState) {
    return pipe(
        assocPath([library, 'loading'], true),
        assocPath([library, 'toLoad'], false)
    )(state) as LibrariesState;
}

function handleLoaded(library: string, state: LibrariesState) {
    return pipe(
        assocPath([library, 'loaded'], true),
        assocPath([library, 'loading'], false)
    )(state) as LibrariesState;
}

export default function librariesReducer(
    state: LibrariesState = {},
    action: LibrariesAction
): LibrariesState {
    switch (action.type) {
        case LibrariesActions.LOAD:
            return (action.payload as LoadingPayload).libraries.reduce(
                (acc, lib) => handleLoad(lib, acc),
                state
            );
        case LibrariesActions.LOADED:
            return (action.payload as LoadedPayload).libraries.reduce(
                (acc, lib) => handleLoaded(lib, acc),
                state
            );
        case LibrariesActions.TO_LOAD:
            return pipe(
                assocPath(
                    [(action.payload as ToLoadPayload).library, 'toLoad'],
                    true
                )
            )(state) as LibrariesState;
        default:
            return state;
    }
}
