'use strict'

import { combineReducers } from 'redux';
import layout from './layout';
import dependencyGraph from './dependencyGraph';

const reducer = combineReducers({layout, dependencyGraph, paths, requestQueue});

export default reducer;
