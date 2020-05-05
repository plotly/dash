"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = config;

var _constants = require("../actions/constants");

function config() {
  var state = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : null;
  var action = arguments.length > 1 ? arguments[1] : undefined;

  if (action.type === (0, _constants.getAction)('SET_CONFIG')) {
    return action.payload;
  }

  return state;
}