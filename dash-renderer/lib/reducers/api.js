"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = createApiReducer;

var _ramda = require("ramda");

function createApiReducer(store) {
  return function ApiReducer() {
    var state = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
    var action = arguments.length > 1 ? arguments[1] : undefined;
    var newState = state;

    if (action.type === store) {
      var _action$payload = action.payload,
          id = _action$payload.id,
          status = _action$payload.status,
          content = _action$payload.content;
      var newRequest = {
        status: status,
        content: content
      };

      if (Array.isArray(id)) {
        newState = (0, _ramda.assocPath)(id, newRequest, state);
      } else if (id) {
        newState = (0, _ramda.assoc)(id, newRequest, state);
      } else {
        newState = (0, _ramda.mergeRight)(state, newRequest);
      }
    }

    return newState;
  };
}