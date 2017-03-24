'use strict'

import { combineReducers } from 'redux';
import layout from './layout';
import graphs from './dependencyGraph';
import paths from './paths';
import requestQueue from './requestQueue';
import appLifecycle from './appLifecycle';
import {layoutRequest, dependenciesRequest} from './api';

const reducer = combineReducers({
    appLifecycle,
    layout,
    graphs,
    paths,
    requestQueue,
    layoutRequest,
    dependenciesRequest
});

export default reducer;
