"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _callbacks = require("../utils/callbacks");

var _isLoading = require("../actions/isLoading");

var observer = {
  observer: function observer(_ref) {
    var dispatch = _ref.dispatch,
        getState = _ref.getState;

    var _getState = getState(),
        callbacks = _getState.callbacks,
        isLoading = _getState.isLoading;

    var pendingCallbacks = (0, _callbacks.getPendingCallbacks)(callbacks);
    var next = Boolean(pendingCallbacks.length);

    if (isLoading !== next) {
      dispatch((0, _isLoading.setIsLoading)(next));
    }
  },
  inputs: ['callbacks']
};
var _default = observer;
exports["default"] = _default;