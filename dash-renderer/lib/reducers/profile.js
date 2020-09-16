"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _ramda = require("ramda");

var _constants = require("../constants/constants");

function _objectWithoutProperties(source, excluded) { if (source == null) return {}; var target = _objectWithoutPropertiesLoose(source, excluded); var key, i; if (Object.getOwnPropertySymbols) { var sourceSymbolKeys = Object.getOwnPropertySymbols(source); for (i = 0; i < sourceSymbolKeys.length; i++) { key = sourceSymbolKeys[i]; if (excluded.indexOf(key) >= 0) continue; if (!Object.prototype.propertyIsEnumerable.call(source, key)) continue; target[key] = source[key]; } } return target; }

function _objectWithoutPropertiesLoose(source, excluded) { if (source == null) return {}; var target = {}; var sourceKeys = Object.keys(source); var key, i; for (i = 0; i < sourceKeys.length; i++) { key = sourceKeys[i]; if (excluded.indexOf(key) >= 0) continue; target[key] = source[key]; } return target; }

var defaultProfile = {
  count: 0,
  total: 0,
  compute: 0,
  network: {
    time: 0,
    upload: 0,
    download: 0
  },
  resources: {},
  status: {
    latest: null
  },
  result: {}
};
var defaultState = {
  updated: [],
  resources: {},
  callbacks: {},
  graphLayout: null
};

var profile = function profile() {
  var state = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : defaultState;
  var action = arguments.length > 1 ? arguments[1] : undefined;

  if (action.type === 'UPDATE_RESOURCE_USAGE') {
    // Keep a record of the most recent change. This
    // is subtly different from history.present becasue
    // it watches all props, not just inputs.
    var _action$payload = action.payload,
        id = _action$payload.id,
        usage = _action$payload.usage,
        status = _action$payload.status;
    var statusMapped = _constants.STATUSMAP[status] || status; // Keep track of the callback that actually changed.

    var newState = {
      updated: [id],
      resources: state.resources,
      callbacks: state.callbacks,
      // graphLayout is never passed in via actions, because we don't
      // want it to trigger a rerender of the callback graph.
      // See CallbackGraphContainer.react
      graphLayout: state.graphLayout
    };
    newState.callbacks[id] = newState.callbacks[id] || (0, _ramda.clone)(defaultProfile);
    var cb = newState.callbacks[id];
    var cbResources = cb.resources;
    var totalResources = newState.resources; // Update resource usage & params.

    cb.count += 1;
    cb.status.latest = statusMapped;
    cb.status[statusMapped] = (cb.status[statusMapped] || 0) + 1;
    cb.result = action.payload.result;
    cb.inputs = action.payload.inputs;
    cb.state = action.payload.state;

    if (usage) {
      var __dash_client = usage.__dash_client,
          __dash_server = usage.__dash_server,
          __dash_upload = usage.__dash_upload,
          __dash_download = usage.__dash_download,
          user = _objectWithoutProperties(usage, ["__dash_client", "__dash_server", "__dash_upload", "__dash_download"]);

      cb.total += __dash_client;
      cb.compute += __dash_server;
      cb.network.time += __dash_client - __dash_server;
      cb.network.upload += __dash_upload;
      cb.network.download += __dash_download;

      for (var r in user) {
        if (user.hasOwnProperty(r)) {
          cbResources[r] = (cbResources[r] || 0) + user[r];
          totalResources[r] = (totalResources[r] || 0) + user[r];
        }
      }
    }

    return newState;
  }

  return state;
};

var _default = profile;
exports["default"] = _default;