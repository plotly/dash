"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;
var initialGraph = {};

var graphs = function graphs() {
  var state = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : initialGraph;
  var action = arguments.length > 1 ? arguments[1] : undefined;

  if (action.type === 'SET_GRAPHS') {
    return action.payload;
  }

  return state;
};

var _default = graphs;
exports["default"] = _default;