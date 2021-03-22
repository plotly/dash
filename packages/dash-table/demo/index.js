import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

import Logger, {DebugLevel, LogLevel} from 'core/Logger';

Logger.setDebugLevel(DebugLevel.DEBUG);
Logger.setLogLevel(LogLevel.NONE);

ReactDOM.render(<App />, document.getElementById('root'));
