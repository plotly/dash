"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.setLoadingMap = void 0;

var _reduxActions = require("redux-actions");

var _loadingMap = require("../reducers/loadingMap");

var setLoadingMap = (0, _reduxActions.createAction)(_loadingMap.LoadingMapActionType.Set);
exports.setLoadingMap = setLoadingMap;