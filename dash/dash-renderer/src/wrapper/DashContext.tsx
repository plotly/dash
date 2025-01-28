import React, {useCallback, useContext, useMemo} from 'react';
import {useStore, useSelector, useDispatch} from 'react-redux';
import {concat, pathOr} from 'ramda';

import {DashLayoutPath} from '../types/component';
import {LoadingPayload} from '../actions/loading';

type LoadingFilterFunc = (loading: LoadingPayload) => boolean;

type LoadingOptions = {
    /**
     *
     */
    extraPath?: DashLayoutPath;
    /**
     *
     */
    rawPath?: boolean;
    /**
     * Function used to filter the properties of the loading component.
     */
    filterFunc?: LoadingFilterFunc;
};

type DashContextType = {
    componentPath: DashLayoutPath;

    isLoading: (options?: LoadingOptions) => boolean;
    useLoading: (options?: LoadingOptions) => boolean;

    // Give access to the right store.
    useSelector: typeof useSelector;
    useDispatch: typeof useDispatch;
    useStore: typeof useStore;
};

export const DashContext = React.createContext<DashContextType>({} as any);

type DashContextProviderProps = {
    children: JSX.Element;
    componentPath: DashLayoutPath;
};

export function DashContextProvider(props: DashContextProviderProps) {
    const {children, componentPath} = props;

    const stringPath = useMemo<string>(
        () => JSON.stringify(componentPath),
        [componentPath]
    );
    const store = useStore();

    const isLoading = useCallback(
        (options?: LoadingOptions) => {
            const {extraPath, rawPath, filterFunc} = options || {};
            let loadingPath = [stringPath];
            if (extraPath) {
                loadingPath = [
                    JSON.stringify(concat(componentPath, extraPath))
                ];
            } else if (rawPath) {
                loadingPath = [JSON.stringify(rawPath)];
            }
            const loading = pathOr(
                [],
                loadingPath,
                (store.getState() as any).loading
            );
            return filterFunc
                ? loading.filter(filterFunc).length > 0
                : loading.length > 0;
        },
        [stringPath]
    );

    const useLoading = useCallback(
        (options?: LoadingOptions) => {
            const {filterFunc, extraPath, rawPath} = options || {};
            return useSelector((state: any) => {
                let loadingPath = [stringPath];
                if (extraPath) {
                    loadingPath = [
                        JSON.stringify(concat(componentPath, extraPath))
                    ];
                } else if (rawPath) {
                    loadingPath = [JSON.stringify(rawPath)];
                }
                const load = pathOr([], loadingPath, state.loading);
                if (filterFunc) {
                    return load.filter(filterFunc).length > 0;
                }
                return load.length > 0;
            });
        },
        [stringPath]
    );

    const ctxValue = useMemo(() => {
        return {
            componentPath,
            isLoading,
            useLoading,

            useSelector,
            useStore,
            useDispatch
        };
    }, [stringPath]);

    return (
        <DashContext.Provider value={ctxValue}>{children}</DashContext.Provider>
    );
}

export function useDashContext() {
    return useContext(DashContext);
}
