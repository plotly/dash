/*eslint-env browser */

'use strict';

import React from 'react';
import ReactDOM from 'react-dom';
import AppProvider from './AppProvider.react';
require('es6-promise').polyfill();


ReactDOM.render(
    <AppProvider/>,
    document.getElementById('react-entry-point')
);
