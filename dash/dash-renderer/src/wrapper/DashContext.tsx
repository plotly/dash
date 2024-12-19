import React, {useCallback, useContext, useMemo} from 'react';
import {useStore, useSelector, useDispatch} from 'react-redux';
import {pathOr} from 'ramda';

import {DashLayoutPath} from '../types/component';

type DashContextType = {
    componentPath: DashLayoutPath;

    isLoading: () => boolean;
    useLoading: () => boolean;

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

    const isLoading = useCallback(() => {
        const loading = pathOr(
            [],
            [stringPath],
            (store.getState() as any).loading
        );
        return loading.length > 0;
    }, [stringPath]);

    const useLoading = useCallback(() => {
        return useSelector((state: any) => {
            const load = pathOr([], [stringPath], state.loading);
            return load.length > 0;
        });
    }, [stringPath]);

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
