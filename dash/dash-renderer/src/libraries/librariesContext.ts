import {createContext, useEffect, useState} from 'react';
import {pathOr, toPairs} from 'ramda';
import loadLibrary from './loadLibrary';
import {batch, useDispatch, useSelector} from 'react-redux';
import {LibrariesState} from './libraryTypes';
import {
    setLibraryLoaded,
    setLibraryLoading,
    setLibraryToLoad
} from '../actions/libraries';
import fetchDist from './fetchDist';

export type LibrariesContextType = {
    state: LibrariesState;
    isLoading: (libraryName: string) => boolean;
    isLoaded: (libraryName: string) => boolean;
    fetchLibraries: () => void;
    getLibrariesToLoad: () => string[];
    addToLoad: (libName: string) => void;
};

function librarySelector(s: any) {
    return s.libraries as LibrariesState;
}

export function createLibrariesContext(
    pathnamePrefix: string,
    initialLibraries: string[],
    onReady: () => void,
    ready: boolean
): LibrariesContextType {
    const dispatch = useDispatch();
    const state = useSelector(librarySelector);
    const [callback, setCallback] = useState<number>(-1);

    const isLoaded = (libraryName: string) =>
        pathOr(false, [libraryName, 'loaded'], state);
    const isLoading = (libraryName: string) =>
        pathOr(false, [libraryName, 'loading'], state);

    const addToLoad = (libraryName: string) => {
        const lib = state[libraryName];
        if (!lib) {
            // Check if already loaded on the window
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            if (window[libraryName]) {
                dispatch(setLibraryLoaded({libraries: [libraryName]}));
            } else {
                dispatch(setLibraryToLoad({library: libraryName}));
            }
        }
        // if lib is already in don't do anything.
    };

    const getLibrariesToLoad = () =>
        toPairs(state).reduce((acc: string[], [key, value]) => {
            if (value.toLoad) {
                acc.push(key);
            }
            return acc;
        }, []);

    const fetchLibraries = () => {
        const libraries = getLibrariesToLoad();
        if (!libraries.length) {
            return;
        }

        dispatch(setLibraryLoading({libraries}));

        fetchDist(pathnamePrefix, libraries)
            .then(data => {
                return Promise.all(data.map(loadLibrary));
            })
            .then(() => {
                dispatch(setLibraryLoaded({libraries}));
                setCallback(-1);
                onReady();
            });
    };

    useEffect(() => {
        batch(() => {
            const loaded: string[] = [];
            initialLibraries.forEach(lib => {
                // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                // @ts-ignore
                if (window[lib]) {
                    loaded.push(lib);
                } else {
                    dispatch(setLibraryToLoad({library: lib}));
                }
            });
            if (loaded.length) {
                dispatch(setLibraryLoaded({libraries: loaded}));
            }
            if (loaded.length === initialLibraries.length) {
                onReady();
            }
        });
    }, [initialLibraries]);

    // Load libraries on a throttle to have time to gather all the components in one go.
    useEffect(() => {
        if (ready) {
            return;
        }
        const libraries = getLibrariesToLoad();
        if (!libraries.length) {
            return;
        }
        if (callback > 0) {
            window.clearTimeout(callback);
        }
        const timeout = window.setTimeout(fetchLibraries, 0);
        setCallback(timeout);
    }, [state, ready, initialLibraries]);

    return {
        state,
        isLoaded,
        isLoading,
        fetchLibraries,
        getLibrariesToLoad,
        addToLoad
    };
}

// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
export const LibrariesContext = createContext<LibrariesContextType>(null);
