import React, {JSX, useEffect, useState} from 'react';

import {createLibrariesContext, LibrariesContext} from './librariesContext';
import {crawlLayout} from '../actions/utils';
import {isEmpty} from 'ramda';

type LibrariesManagerProps = {
    children: JSX.Element;
    requests_pathname_prefix: string;
    onReady: () => void;
    ready: boolean;
    layout?: any;
    initialLibraries?: string[];
};

const LibraryProvider = (props: LibrariesManagerProps) => {
    const {
        children,
        requests_pathname_prefix,
        onReady,
        ready,
        initialLibraries
    } = props;
    const contextValue = createLibrariesContext(
        requests_pathname_prefix,
        initialLibraries as string[],
        onReady,
        ready
    );
    return (
        <LibrariesContext.Provider value={contextValue}>
            {children}
        </LibrariesContext.Provider>
    );
};

const LibraryManager = (props: LibrariesManagerProps) => {
    const {children, ready, layout} = props;

    const [initialLibraries, setInitialLibraries] = useState<string[] | null>(
        null
    );

    useEffect(() => {
        if (layout && !isEmpty(layout) && !ready && !initialLibraries) {
            const libraries: string[] = [];
            crawlLayout(layout, (child: any) => {
                if (child.namespace && !libraries.includes(child.namespace)) {
                    libraries.push(child.namespace);
                }
            });
            setInitialLibraries(libraries);
        }
    }, [layout, ready, initialLibraries]);

    if (!initialLibraries) {
        return children;
    }

    return (
        <LibraryProvider {...props} initialLibraries={initialLibraries}>
            {children}
        </LibraryProvider>
    );
};

export default LibraryManager;
