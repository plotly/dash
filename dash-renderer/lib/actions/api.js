"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = apiThunk;

var _ramda = require("ramda");

var _actions = require("../actions");

var _utils = require("./utils");

/* eslint-disable-next-line no-console */
var logWarningOnce = (0, _ramda.once)(console.warn);

function GET(path, fetchConfig) {
  return fetch(path, (0, _ramda.mergeDeepRight)(fetchConfig, {
    method: 'GET',
    headers: (0, _actions.getCSRFHeader)()
  }));
}

function POST(path, fetchConfig) {
  var body = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
  return fetch(path, (0, _ramda.mergeDeepRight)(fetchConfig, {
    method: 'POST',
    headers: (0, _actions.getCSRFHeader)(),
    body: body ? JSON.stringify(body) : null
  }));
}

var request = {
  GET: GET,
  POST: POST
};

function apiThunk(endpoint, method, store, id, body) {
  return function (dispatch, getState) {
    var _getState = getState(),
        config = _getState.config;

    var url = "".concat((0, _utils.urlBase)(config)).concat(endpoint);

    function setConnectionStatus(connected) {
      if (getState().error.backEndConnected !== connected) {
        dispatch({
          type: 'SET_CONNECTION_STATUS',
          payload: connected
        });
      }
    }

    dispatch({
      type: store,
      payload: {
        id: id,
        status: 'loading'
      }
    });
    return request[method](url, config.fetch, body).then(function (res) {
      setConnectionStatus(true);
      var contentType = res.headers.get('content-type');

      if (contentType && contentType.indexOf('application/json') !== -1) {
        return res.json().then(function (json) {
          dispatch({
            type: store,
            payload: {
              status: res.status,
              content: json,
              id: id
            }
          });
          return json;
        });
      }

      logWarningOnce('Response is missing header: content-type: application/json');
      return dispatch({
        type: store,
        payload: {
          id: id,
          status: res.status
        }
      });
    }, function () {
      // fetch rejection - this means the request didn't return,
      // we don't get here from 400/500 errors, only network
      // errors or unresponsive servers.
      setConnectionStatus(false);
    })["catch"](function (err) {
      var message = 'Error from API call: ' + endpoint;
      (0, _actions.handleAsyncError)(err, message, dispatch);
    });
  };
}