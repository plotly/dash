export enum LibrariesActions {
    LOAD = 'LOAD_LIBRARY',
    LOADED = 'LOADED_LIBRARY',
    TO_LOAD = 'TO_LOAD'
}

export type LibrariesState = {
    [libname: string]: {
        toLoad: boolean;
        loading: boolean;
        loaded: boolean;
    };
};
export type LibraryResource = {
    type: '_js_dist' | '_css_dist';
    url: string;
};
