"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.computePaths = computePaths;
exports.getPath = getPath;

var _ramda = require("ramda");

var _utils = require("./utils");

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

/*
 * state.paths has structure:
 * {
 *   strs: {[id]: path} // for regular string ids
 *   objs: {[keyStr]: [{values, path}]} // for wildcard ids
 * }
 * keyStr: sorted keys of the id, joined with ',' into one string
 * values: array of values in the id, in order of keys
 */
function computePaths(subTree, startingPath, oldPaths, events) {
  var _ref = oldPaths || {
    strs: {},
    objs: {}
  },
      oldStrs = _ref.strs,
      oldObjs = _ref.objs;

  var diffHead = function diffHead(path) {
    return startingPath.some(function (v, i) {
      return path[i] !== v;
    });
  };

  var spLen = startingPath.length; // if we're updating a subtree, clear out all of the existing items

  var strs = spLen ? (0, _ramda.filter)(diffHead, oldStrs) : {};
  var objs = {};

  if (spLen) {
    (0, _ramda.forEachObjIndexed)(function (oldValPaths, oldKeys) {
      var newVals = (0, _ramda.filter)(function (_ref2) {
        var path = _ref2.path;
        return diffHead(path);
      }, oldValPaths);

      if (newVals.length) {
        objs[oldKeys] = newVals;
      }
    }, oldObjs);
  }

  (0, _utils.crawlLayout)(subTree, function assignPath(child, itempath) {
    var id = (0, _ramda.path)(['props', 'id'], child);

    if (id) {
      if (_typeof(id) === 'object') {
        var keys = Object.keys(id).sort();
        var values = (0, _ramda.props)(keys, id);
        var keyStr = keys.join(',');
        var paths = objs[keyStr] = objs[keyStr] || [];
        paths.push({
          values: values,
          path: (0, _ramda.concat)(startingPath, itempath)
        });
      } else {
        strs[id] = (0, _ramda.concat)(startingPath, itempath);
      }
    }
  }); // We include an event emitter here because it will be used along with
  // paths to determine when the app is ready for callbacks.

  return {
    strs: strs,
    objs: objs,
    events: events || oldPaths.events
  };
}

function getPath(paths, id) {
  if (_typeof(id) === 'object') {
    var keys = Object.keys(id).sort();
    var keyStr = keys.join(',');
    var keyPaths = paths.objs[keyStr];

    if (!keyPaths) {
      return false;
    }

    var values = (0, _ramda.props)(keys, id);
    var pathObj = (0, _ramda.find)((0, _ramda.propEq)('values', values), keyPaths);
    return pathObj && pathObj.path;
  }

  return paths.strs[id];
}