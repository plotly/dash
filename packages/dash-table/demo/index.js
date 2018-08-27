import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

import Logger, { DebugLevel, LogLevel } from 'core/Logger';

Logger.setDebugLevel(DebugLevel.NONE);
Logger.setLogLevel(LogLevel.WARNING);

ReactDOM.render(<App />, document.getElementById('root'));
