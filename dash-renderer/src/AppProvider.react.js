import React, {useEffect, useRef} from 'react';
import {Provider} from 'react-redux';

import initializeStore from './store';
import AppContainer from './AppContainer.react';

import PropTypes from 'prop-types';



const AppProvider = ({hooks, dashConfig}) => {

    const store = useRef(initializeStore(true));

    return (
        <Provider store={store.current}>
            <AppContainer dashConfig={dashConfig} hooks={hooks} />
        </Provider>
    );
};

AppProvider.propTypes = {
    dashConfig: PropTypes.object, // the dash config that is originally in the script tag
    hooks: PropTypes.shape({
        request_pre: PropTypes.func,
        request_post: PropTypes.func,
    }),
};

AppProvider.defaultProps = {
    hooks: {
        request_pre: null,
        request_post: null,
    },
};

export default AppProvider;
