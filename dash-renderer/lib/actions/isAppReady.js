"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _ramda = require("ramda");

var _dashComponentPlugins = require("@plotly/dash-component-plugins");

var _registry = _interopRequireDefault(require("../registry"));

var _paths = require("./paths");

var _dependencies = require("./dependencies");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

var _default = function _default(layout, paths, targets) {
  if (!targets.length) {
    return true;
  }

  var promises = [];
  var events = paths.events;
  var rendered = new Promise(function (resolveRendered) {
    events.once('rendered', resolveRendered);
  });
  targets.forEach(function (id) {
    var pathOfId = (0, _paths.getPath)(paths, id);

    if (!pathOfId) {
      return;
    }

    var target = (0, _ramda.path)(pathOfId, layout);

    if (!target) {
      return;
    }

    var component = _registry["default"].resolve(target);

    var ready = (0, _dashComponentPlugins.isReady)(component);

    if (ready && typeof ready.then === 'function') {
      promises.push(Promise.race([ready, rendered.then(function () {
        return document.getElementById((0, _dependencies.stringifyId)(id)) && ready;
      })]));
    }
  });
  return promises.length ? Promise.all(promises) : true;
};

exports["default"] = _default;