"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = error;

var _ramda = require("ramda");

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) return _arrayLikeToArray(arr); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

var initialError = {
  frontEnd: [],
  backEnd: [],
  backEndConnected: true
};

function error() {
  var state = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : initialError;
  var action = arguments.length > 1 ? arguments[1] : undefined;

  switch (action.type) {
    case 'ON_ERROR':
      {
        var frontEnd = state.frontEnd,
            backEnd = state.backEnd,
            backEndConnected = state.backEndConnected; // log errors to the console for stack tracing and so they're
        // available even with debugging off

        /* eslint-disable-next-line no-console */

        console.error(action.payload.error);

        if (action.payload.type === 'frontEnd') {
          return {
            frontEnd: [(0, _ramda.mergeRight)(action.payload, {
              timestamp: new Date()
            })].concat(_toConsumableArray(frontEnd)),
            backEnd: backEnd,
            backEndConnected: backEndConnected
          };
        } else if (action.payload.type === 'backEnd') {
          return {
            frontEnd: frontEnd,
            backEnd: [(0, _ramda.mergeRight)(action.payload, {
              timestamp: new Date()
            })].concat(_toConsumableArray(backEnd)),
            backEndConnected: backEndConnected
          };
        }

        return state;
      }

    case 'SET_CONNECTION_STATUS':
      {
        return (0, _ramda.mergeRight)(state, {
          backEndConnected: action.payload
        });
      }

    default:
      {
        return state;
      }
  }
}