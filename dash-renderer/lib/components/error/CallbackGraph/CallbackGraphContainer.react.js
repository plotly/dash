"use strict";

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.CallbackGraphContainer = void 0;

var _react = _interopRequireWildcard(require("react"));

var _propTypes = _interopRequireDefault(require("prop-types"));

require("./CallbackGraphContainer.css");

var _viz = _interopRequireDefault(require("viz.js"));

var _full = require("viz.js/full.render");

var _dependencies = require("../../../actions/dependencies");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function _getRequireWildcardCache() { if (typeof WeakMap !== "function") return null; var cache = new WeakMap(); _getRequireWildcardCache = function _getRequireWildcardCache() { return cache; }; return cache; }

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } if (obj === null || _typeof(obj) !== "object" && typeof obj !== "function") { return { "default": obj }; } var cache = _getRequireWildcardCache(); if (cache && cache.has(obj)) { return cache.get(obj); } var newObj = {}; var hasPropertyDescriptor = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) { var desc = hasPropertyDescriptor ? Object.getOwnPropertyDescriptor(obj, key) : null; if (desc && (desc.get || desc.set)) { Object.defineProperty(newObj, key, desc); } else { newObj[key] = obj[key]; } } } newObj["default"] = obj; if (cache) { cache.set(obj, newObj); } return newObj; }

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance"); }

function _iterableToArrayLimit(arr, i) { if (!(Symbol.iterator in Object(arr) || Object.prototype.toString.call(arr) === "[object Arguments]")) { return; } var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

var CallbackGraphContainer = function CallbackGraphContainer(_ref) {
  var graphs = _ref.graphs;
  var el = (0, _react.useRef)(null);
  var viz = (0, _react.useRef)(null);

  var makeViz = function makeViz() {
    viz.current = new _viz["default"]({
      Module: _full.Module,
      render: _full.render
    });
  };

  if (!viz.current) {
    makeViz();
  }

  (0, _react.useEffect)(function () {
    var callbacks = graphs.callbacks;
    var elements = {};
    var callbacksOut = [];
    var links = callbacks.map(function (_ref2, i) {
      var inputs = _ref2.inputs,
          outputs = _ref2.outputs;
      callbacksOut.push("cb".concat(i, ";"));

      function recordAndReturn(_ref3) {
        var id = _ref3.id,
            property = _ref3.property;
        var idClean = (0, _dependencies.stringifyId)(id).replace(/[\{\}".;\[\]()]/g, '').replace(/:/g, '-').replace(/,/g, '_');
        elements[idClean] = elements[idClean] || {};
        elements[idClean][property] = true;
        return "\"".concat(idClean, ".").concat(property, "\"");
      }

      var out_nodes = outputs.map(recordAndReturn).join(', ');
      var in_nodes = inputs.map(recordAndReturn).join(', ');
      return "{".concat(in_nodes, "} -> cb").concat(i, " -> {").concat(out_nodes, "};");
    });
    var dot = "digraph G {\n            overlap = false; fontname=\"Arial\"; fontcolor=\"#333333\";\n            edge [color=\"#888888\"];\n            node [shape=box, fontname=\"Arial\", style=filled, color=\"#109DFF\", fontcolor=white];\n            graph [penwidth=0];\n            subgraph callbacks {\n                node [shape=circle, width=0.3, label=\"\", color=\"#00CC96\"];\n                ".concat(callbacksOut.join('\n'), " }\n\n            ").concat(Object.entries(elements).map(function (_ref4, i) {
      var _ref5 = _slicedToArray(_ref4, 2),
          id = _ref5[0],
          props = _ref5[1];

      return "\n                subgraph cluster_".concat(i, " {\n                    bgcolor=\"#B9C2CE\";\n                    ").concat(Object.keys(props).map(function (p) {
        return "\"".concat(id, ".").concat(p, "\" [label=\"").concat(p, "\"];");
      }).join('\n'), "\n                    label = \"").concat(id, "\"; }");
    }).join('\n'), "\n\n            ").concat(links.join('\n'), " }");
    viz.current.renderSVGElement(dot).then(function (vizEl) {
      el.current.innerHTML = '';
      el.current.appendChild(vizEl);
    })["catch"](function (e) {
      // https://github.com/mdaines/viz.js/wiki/Caveats
      makeViz(); // eslint-disable-next-line no-console

      console.error(e);
      el.current.innerHTML = 'Error creating callback graph';
    });
  });
  return _react["default"].createElement("div", {
    className: "dash-callback-dag--container",
    ref: el
  });
};

exports.CallbackGraphContainer = CallbackGraphContainer;
CallbackGraphContainer.propTypes = {
  graphs: _propTypes["default"].object
};