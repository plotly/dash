"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.STATUSMAP = exports.STATUS = exports.OAUTH_COOKIE_NAME = exports.REDIRECT_URI_PATHNAME = void 0;

var _STATUSMAP;

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

var REDIRECT_URI_PATHNAME = '/_oauth2/callback';
exports.REDIRECT_URI_PATHNAME = REDIRECT_URI_PATHNAME;
var OAUTH_COOKIE_NAME = 'plotly_oauth_token';
exports.OAUTH_COOKIE_NAME = OAUTH_COOKIE_NAME;
var STATUS = {
  OK: 200,
  PREVENT_UPDATE: 204,
  CLIENTSIDE_ERROR: 'CLIENTSIDE_ERROR',
  NO_RESPONSE: 'NO_RESPONSE'
};
exports.STATUS = STATUS;
var STATUSMAP = (_STATUSMAP = {}, _defineProperty(_STATUSMAP, STATUS.OK, 'SUCCESS'), _defineProperty(_STATUSMAP, STATUS.PREVENT_UPDATE, 'NO_UPDATE'), _STATUSMAP);
exports.STATUSMAP = STATUSMAP;