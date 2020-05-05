"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _constants = require("../actions/constants");

var initialPaths = {
  strs: {},
  objs: {}
};

var paths = function paths() {
  var state = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : initialPaths;
  var action = arguments.length > 1 ? arguments[1] : undefined;

  if (action.type === (0, _constants.getAction)('SET_PATHS')) {
    return action.payload;
  }

  return state;
};

var _default = paths;
exports["default"] = _default;