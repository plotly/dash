'use strict'

import { combineReducers } from 'redux';
import layout from './layout';
import graphs from './dependencyGraph';
import paths from './paths';
import requestQueue from './requestQueue';

const reducer = combineReducers({layout, graphs, paths, requestQueue});

export default reducer;
