"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var pendingCallbacks = function pendingCallbacks() {
  var state = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];
  var action = arguments.length > 1 ? arguments[1] : undefined;

  switch (action.type) {
    case 'SET_PENDING_CALLBACKS':
      return action.payload;

    default:
      return state;
  }
};

var _default = pendingCallbacks;
exports["default"] = _default;