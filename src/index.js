/*eslint-env browser */

'use strict';

import React from 'react';
import ReactDOM from 'react-dom';
import AppContainer from './AppContainer.react';
require('es6-promise').polyfill();


ReactDOM.render(
    <AppContainer/>,
    document.getElementById('react-entry-point')
);
