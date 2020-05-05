"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance"); }

function _iterableToArray(iter) { if (Symbol.iterator in Object(iter) || Object.prototype.toString.call(iter) === "[object Arguments]") return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = new Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } }

var initialHistory = {
  past: [],
  present: {},
  future: []
};

function history() {
  var state = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : initialHistory;
  var action = arguments.length > 1 ? arguments[1] : undefined;

  switch (action.type) {
    case 'UNDO':
      {
        var past = state.past,
            present = state.present,
            future = state.future;
        var previous = past[past.length - 1];
        var newPast = past.slice(0, past.length - 1);
        return {
          past: newPast,
          present: previous,
          future: [present].concat(_toConsumableArray(future))
        };
      }

    case 'REDO':
      {
        var _past = state.past,
            _present = state.present,
            _future = state.future;
        var next = _future[0];

        var newFuture = _future.slice(1);

        return {
          past: [].concat(_toConsumableArray(_past), [_present]),
          present: next,
          future: newFuture
        };
      }

    case 'REVERT':
      {
        var _past2 = state.past,
            _future2 = state.future;
        var _previous = _past2[_past2.length - 1];

        var _newPast = _past2.slice(0, _past2.length - 1);

        return {
          past: _newPast,
          present: _previous,
          future: _toConsumableArray(_future2)
        };
      }

    default:
      {
        return state;
      }
  }
}

var _default = history;
exports["default"] = _default;