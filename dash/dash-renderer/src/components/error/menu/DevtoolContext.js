import React, {useContext, useMemo, useState} from 'react';

export const DevtoolContext = React.createContext({});

export const DevtoolProvider = ({children}) => {
    const [popup, setPopup] = useState('');

    return (
        <DevtoolContext.Provider
            value={{
                popup,
                setPopup
            }}
        >
            {children}
        </DevtoolContext.Provider>
    );
};

export const useDevtool = () => {
    return useContext(DevtoolContext);
};

export const useDevtoolMenuButtonClassName = popupName => {
    const {popup} = useDevtool();

    const className = useMemo(() => {
        const base = 'dash-debug-menu__button';
        if (popup === popupName) {
            return base + ' dash-debug-menu__button--selected';
        }
        return base;
    }, [popup]);

    return className;
};
