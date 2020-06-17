"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.setIsLoading = void 0;

var _reduxActions = require("redux-actions");

var _isLoading = require("../reducers/isLoading");

var setIsLoading = (0, _reduxActions.createAction)(_isLoading.IsLoadingActionType.Set);
exports.setIsLoading = setIsLoading;