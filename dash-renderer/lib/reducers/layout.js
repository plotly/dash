"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _ramda = require("ramda");

var _constants = require("../actions/constants");

var layout = function layout() {
  var state = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
  var action = arguments.length > 1 ? arguments[1] : undefined;

  if (action.type === (0, _constants.getAction)('SET_LAYOUT')) {
    return action.payload;
  } else if ((0, _ramda.includes)(action.type, ['UNDO_PROP_CHANGE', 'REDO_PROP_CHANGE', (0, _constants.getAction)('ON_PROP_CHANGE')])) {
    var propPath = (0, _ramda.append)('props', action.payload.itempath);
    var existingProps = (0, _ramda.view)((0, _ramda.lensPath)(propPath), state);
    var mergedProps = (0, _ramda.mergeRight)(existingProps, action.payload.props);
    return (0, _ramda.assocPath)(propPath, mergedProps, state);
  }

  return state;
};

var _default = layout;
exports["default"] = _default;