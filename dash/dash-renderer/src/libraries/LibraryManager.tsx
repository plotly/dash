import React, {JSX} from 'react';

import {createLibrariesContext, LibrariesContext} from './librariesContext';

type LibrariesManagerProps = {
    children: JSX.Element;
    requests_pathname_prefix: string;
};

const LibraryManager = (props: LibrariesManagerProps) => {
    const {children, requests_pathname_prefix} = props;
    const contextValue = createLibrariesContext(requests_pathname_prefix);

    return (
        <LibrariesContext.Provider value={contextValue}>
            {children}
        </LibrariesContext.Provider>
    );
};

export default LibraryManager;
