"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;
var initialChange = {
  id: null,
  props: {}
};

function changed() {
  var state = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : initialChange;
  // This is empty just to initialize the store. Changes
  // are actually recorded in reducer.js so that we can
  // resolve paths to id.
  return state;
}

var _default = changed;
exports["default"] = _default;