"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _ramda = require("ramda");

var SIMPLE_COMPONENT_TYPES = ['String', 'Number', 'Null', 'Boolean'];

var _default = function _default(component) {
  return (0, _ramda.includes)((0, _ramda.type)(component), SIMPLE_COMPONENT_TYPES);
};

exports["default"] = _default;