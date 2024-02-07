import {
    createContext,
    useContext,
    useReducer,
    useEffect,
    useState
} from 'react';
import {assocPath, pathOr, pipe, toPairs} from 'ramda';

type LibraryResource = {
    type: '_js_dist' | '_css_dist';
    url: string;
    async?: string;
    namespace: string;
    relative_package_path?: string;
};

type LibrariesState = {
    [libname: string]: {
        toLoad: boolean;
        loading: boolean;
        loaded: boolean;
        dist?: LibraryResource[];
    };
};

enum LibrariesActions {
    LOAD,
    LOADED,
    TO_LOAD
}

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

export type LibrariesContextType = {
    state: LibrariesState;
    setLoading: (payload: LoadingPayload) => void;
    setLoaded: (payload: LoadedPayload) => void;
    setToLoad: (payload: ToLoadPayload) => void;
    isLoading: (libraryName: string) => boolean;
    isLoaded: (libraryName: string) => boolean;
    fetchLibraries: () => void;
    getLibrariesToLoad: () => string[];
    addToLoad: (libName: string) => void;
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

export function librariesReducer(
    state: LibrariesState,
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

export function createLibrariesContext(
    pathnamePrefix: string,
    initialLibraries: string[],
    onReady: () => void,
    ready: boolean
): LibrariesContextType {
    const [state, dispatch] = useReducer(librariesReducer, {}, () => {
        const libState: LibrariesState = {};
        initialLibraries.forEach(lib => {
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            if (window[lib]) {
                libState[lib] = {toLoad: false, loaded: true, loading: false};
            } else {
                libState[lib] = {toLoad: true, loaded: false, loading: false};
            }
        });
        return libState;
    });
    const [callback, setCallback] = useState<number>(-1);
    const createAction = (type: LibrariesActions) => (payload: any) =>
        dispatch({type, payload});

    const setLoading = createAction(LibrariesActions.LOAD);
    const setLoaded = createAction(LibrariesActions.LOADED);
    const setToLoad = createAction(LibrariesActions.TO_LOAD);

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
                setLoaded({libraries: [libraryName]});
            } else {
                setToLoad({library: libraryName});
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

        setLoading({libraries});

        fetch(`${pathnamePrefix}_dash-dist`, {
            body: JSON.stringify(libraries),
            headers: {'Content-Type': 'application/json'},
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                const head = document.querySelector('head');
                const loadPromises: Promise<void>[] = [];
                data.forEach((resource: LibraryResource) => {
                    if (resource.type === '_js_dist') {
                        const element = document.createElement('script');
                        element.src = resource.url;
                        element.async = true;
                        loadPromises.push(
                            new Promise((resolve, reject) => {
                                element.onload = () => {
                                    resolve();
                                };
                                element.onerror = error => reject(error);
                            })
                        );
                        head?.appendChild(element);
                    } else if (resource.type === '_css_dist') {
                        const element = document.createElement('link');
                        element.href = resource.url;
                        element.rel = 'stylesheet';
                        loadPromises.push(
                            new Promise((resolve, reject) => {
                                element.onload = () => {
                                    resolve();
                                };
                                element.onerror = error => reject(error);
                            })
                        );
                        head?.appendChild(element);
                    }
                });
                return Promise.all(loadPromises);
            })
            .then(() => {
                setLoaded({libraries});
                setCallback(-1);
                onReady();
            });
    };

    // Load libraries on a throttle to have time to gather all the components in one go.
    useEffect(() => {
        const libraries = getLibrariesToLoad();
        if (!libraries.length) {
            if (!ready && initialLibraries.length === 0) {
                onReady();
            }
            return;
        }
        if (callback > 0) {
            window.clearTimeout(callback);
        }
        const timeout = window.setTimeout(fetchLibraries, 0);
        setCallback(timeout);
    }, [state]);

    return {
        state,
        setLoading,
        setLoaded,
        setToLoad,
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

export function useDashLibraries() {
    return useContext(LibrariesContext);
}
