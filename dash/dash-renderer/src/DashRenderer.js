import React from 'react';
import ReactDOM from 'react-dom';

import AppProvider from './AppProvider.react';

class DashRenderer {
    constructor(hooks) {
        // render Dash Renderer upon initialising!
        const container = document.getElementById('react-entry-point');

        if (ReactDOM.createRoot) {
            const root = ReactDOM.createRoot(container);
            root.render(<AppProvider hooks={hooks} />);
        } else {
            ReactDOM.render(<AppProvider hooks={hooks} />, container);
        }
    }
}

export {DashRenderer};
