"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.STATUS = exports.OAUTH_COOKIE_NAME = exports.REDIRECT_URI_PATHNAME = void 0;
var REDIRECT_URI_PATHNAME = '/_oauth2/callback';
exports.REDIRECT_URI_PATHNAME = REDIRECT_URI_PATHNAME;
var OAUTH_COOKIE_NAME = 'plotly_oauth_token';
exports.OAUTH_COOKIE_NAME = OAUTH_COOKIE_NAME;
var STATUS = {
  OK: 200,
  PREVENT_UPDATE: 204,
  CLIENTSIDE_ERROR: 'CLIENTSIDE_ERROR'
};
exports.STATUS = STATUS;