/*eslint-env browser */

'use strict';

import React from 'react';
import ReactDOM from 'react-dom';
import Container from './container.react.js';

import { Provider } from 'react-redux'
import { createStore } from 'redux'
import reducer from './reducers/reducer.js';

const store = createStore(reducer);

ReactDOM.render(
    <Provider store={store}>
        <Container/>
    </Provider>,
    document.getElementById('react-entry-point')
);
