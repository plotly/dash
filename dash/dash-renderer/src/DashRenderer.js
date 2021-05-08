import React from 'react';
import ReactDOM from 'react-dom';
import AppProvider from './AppProvider.react';

class DashRenderer {
    constructor(hooks) {
        // render Dash Renderer upon initialising!
        ReactDOM.render(
            <AppProvider hooks={hooks} />,
            document.getElementById('react-entry-point')
        );
    }
}

export {DashRenderer};
