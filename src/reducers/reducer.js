'use strict'

import { combineReducers } from 'redux';
import layout from './layout';
import dependencyGraph from './dependencyGraph';
import paths from './paths';
import requestQueue from './requestQueue';

const reducer = combineReducers({layout, dependencyGraph, paths, requestQueue});

export default reducer;
