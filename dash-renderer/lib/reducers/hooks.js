"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var customHooks = function customHooks() {
  var state = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {
    request_pre: null,
    request_post: null,
    bear: false
  };
  var action = arguments.length > 1 ? arguments[1] : undefined;

  switch (action.type) {
    case 'SET_HOOKS':
      return action.payload;

    default:
      return state;
  }
};

var _default = customHooks;
exports["default"] = _default;