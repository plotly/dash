"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.getPendingCallbacks = void 0;

var _ramda = require("ramda");

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance"); }

function _iterableToArray(iter) { if (Symbol.iterator in Object(iter) || Object.prototype.toString.call(iter) === "[object Arguments]") return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = new Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } }

var getPendingCallbacks = function getPendingCallbacks(state) {
  var _Array;

  return (_Array = Array()).concat.apply(_Array, _toConsumableArray((0, _ramda.values)((0, _ramda.omit)(['stored', 'completed'], state))));
};

exports.getPendingCallbacks = getPendingCallbacks;