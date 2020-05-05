"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _constants = require("../actions/constants");

var _constants2 = require("./constants");

function appLifecycle() {
  var state = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : (0, _constants2.getAppState)('STARTED');
  var action = arguments.length > 1 ? arguments[1] : undefined;

  switch (action.type) {
    case (0, _constants.getAction)('SET_APP_LIFECYCLE'):
      return (0, _constants2.getAppState)(action.payload);

    default:
      return state;
  }
}

var _default = appLifecycle;
exports["default"] = _default;