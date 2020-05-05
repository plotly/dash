"use strict";

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _react = _interopRequireDefault(require("react"));

var _ramda = require("ramda");

var _propTypes = _interopRequireDefault(require("prop-types"));

var styles = _interopRequireWildcard(require("./styles/styles.js"));

var constants = _interopRequireWildcard(require("./constants/constants.js"));

function _getRequireWildcardCache() { if (typeof WeakMap !== "function") return null; var cache = new WeakMap(); _getRequireWildcardCache = function _getRequireWildcardCache() { return cache; }; return cache; }

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } if (obj === null || _typeof(obj) !== "object" && typeof obj !== "function") { return { "default": obj }; } var cache = _getRequireWildcardCache(); if (cache && cache.has(obj)) { return cache.get(obj); } var newObj = {}; var hasPropertyDescriptor = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) { var desc = hasPropertyDescriptor ? Object.getOwnPropertyDescriptor(obj, key) : null; if (desc && (desc.get || desc.set)) { Object.defineProperty(newObj, key, desc); } else { newObj[key] = obj[key]; } } } newObj["default"] = obj; if (cache) { cache.set(obj, newObj); } return newObj; }

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

/* eslint-disable-next-line no-console */
var logWarningOnce = (0, _ramda.once)(console.warn);

function AccessDenied(props) {
  var config = props.config;
  var fid = config.fid;
  var owner_username = fid.split(':')[0];
  return _react["default"].createElement("div", {
    style: (0, _ramda.mergeRight)(styles.base.html, styles.base.container)
  }, _react["default"].createElement("div", {
    style: styles.base.h2
  }, "Access Denied"), _react["default"].createElement("div", {
    style: styles.base.h4
  }, "Uh oh! You don't have access to this Dash app."), _react["default"].createElement("div", null, "This app is owned by ", owner_username, ". Reach out to", owner_username, " to grant you access to this app and then try refreshing the app."), _react["default"].createElement("br", null), _react["default"].createElement("a", {
    style: styles.base.a,
    onClick: function onClick() {
      try {
        document.cookie = "".concat(constants.OAUTH_COOKIE_NAME, "=; ") + 'expires=Thu, 01 Jan 1970 00:00:01 GMT;';
      } catch (e) {
        logWarningOnce(e);
      }

      window.location.reload(true);
    }
  }, "Log out of session"));
}

AccessDenied.propTypes = {
  config: _propTypes["default"].object
};
var _default = AccessDenied;
exports["default"] = _default;