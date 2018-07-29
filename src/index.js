/*eslint-env browser */

'use strict';

import React from 'react';
import ReactDOM from 'react-dom';
import AppProvider from './AppProvider.react';
import ErrorHandler from './ErrorHandler.react';


ReactDOM.render(
    <ErrorHandler><AppProvider/></ErrorHandler>,
    document.getElementById('react-entry-point')
);
