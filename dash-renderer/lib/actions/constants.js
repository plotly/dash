"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.getAction = void 0;
var actionList = {
  ON_PROP_CHANGE: 1,
  SET_REQUEST_QUEUE: 1,
  SET_GRAPHS: 1,
  SET_PATHS: 1,
  SET_LAYOUT: 1,
  SET_APP_LIFECYCLE: 1,
  SET_CONFIG: 1,
  ON_ERROR: 1,
  SET_HOOKS: 1
};

var getAction = function getAction(action) {
  if (actionList[action]) {
    return action;
  }

  throw new Error("".concat(action, " is not defined."));
};

exports.getAction = getAction;