"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.getAppState = getAppState;

function getAppState(state) {
  var stateList = {
    STARTED: 'STARTED',
    HYDRATED: 'HYDRATED'
  };

  if (stateList[state]) {
    return stateList[state];
  }

  throw new Error("".concat(state, " is not a valid app state."));
}