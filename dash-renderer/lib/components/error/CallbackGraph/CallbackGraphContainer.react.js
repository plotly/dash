"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.CallbackGraphContainer = void 0;

var _react = _interopRequireWildcard(require("react"));

var _propTypes = _interopRequireDefault(require("prop-types"));

var _reactRedux = require("react-redux");

var _cytoscape = _interopRequireDefault(require("cytoscape"));

var _reactCytoscapejs = _interopRequireDefault(require("react-cytoscapejs"));

var _cytoscapeDagre = _interopRequireDefault(require("cytoscape-dagre"));

var _cytoscapeFcose = _interopRequireDefault(require("cytoscape-fcose"));

var _reactJsonTree = _interopRequireDefault(require("react-json-tree"));

var _ramda = require("ramda");

var _paths = require("../../../actions/paths");

var _dependencies = require("../../../actions/dependencies");

var _actions = require("../../../actions");

require("./CallbackGraphContainer.css");

var _CallbackGraphContainerStylesheet = _interopRequireDefault(require("./CallbackGraphContainerStylesheet"));

var _CallbackGraphEffects = require("./CallbackGraphEffects");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function _getRequireWildcardCache() { if (typeof WeakMap !== "function") return null; var cache = new WeakMap(); _getRequireWildcardCache = function _getRequireWildcardCache() { return cache; }; return cache; }

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } if (obj === null || _typeof(obj) !== "object" && typeof obj !== "function") { return { "default": obj }; } var cache = _getRequireWildcardCache(); if (cache && cache.has(obj)) { return cache.get(obj); } var newObj = {}; var hasPropertyDescriptor = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) { var desc = hasPropertyDescriptor ? Object.getOwnPropertyDescriptor(obj, key) : null; if (desc && (desc.get || desc.set)) { Object.defineProperty(newObj, key, desc); } else { newObj[key] = obj[key]; } } } newObj["default"] = obj; if (cache) { cache.set(obj, newObj); } return newObj; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { var hasNativeReflectConstruct = _isNativeReflectConstruct(); return function _createSuperInternal() { var Super = _getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Date.prototype.toString.call(Reflect.construct(Date, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _unsupportedIterableToArray(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArrayLimit(arr, i) { if (typeof Symbol === "undefined" || !(Symbol.iterator in Object(arr))) return; var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { _defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

_cytoscape["default"].use(_cytoscapeDagre["default"]);

_cytoscape["default"].use(_cytoscapeFcose["default"]);
/*
 * Generates all the elements (nodes, edeges) for the dependency graph.
 */


function generateElements(graphs, profile, extraLinks) {
  var consumed = [];
  var elements = [];
  var structure = {};

  function recordNode(id, property) {
    var idStr = (0, _dependencies.stringifyId)(id);
    var idType = _typeof(id) === 'object' ? 'wildcard' : 'component'; // dagre layout has problems with eg `width` property - so prepend an X

    var parentId = idStr;
    var childId = "".concat(parentId, ".X").concat(property);

    if (!consumed.includes(parentId)) {
      consumed.push(parentId);
      elements.push({
        data: {
          id: parentId,
          label: idStr,
          type: idType
        }
      });
      structure[parentId] = [];
    }

    if (!consumed.includes(childId)) {
      consumed.push(childId);
      elements.push({
        data: {
          id: childId,
          label: property,
          parent: parentId,
          type: 'property'
        }
      });
      structure[parentId].push(childId);
    }

    return childId;
  }

  function recordEdge(source, target, type) {
    elements.push({
      data: {
        source: source,
        target: target,
        type: type
      }
    });
  }

  (graphs.callbacks || []).forEach(function (callback, i) {
    var cb = "__dash_callback__.".concat(callback.output);
    var cbProfile = profile.callbacks[callback.output] || {};
    var count = cbProfile.count || 0;
    var time = cbProfile.total || 0;
    elements.push({
      data: {
        id: cb,
        label: "callback.".concat(i),
        type: 'callback',
        mode: callback.clientside_function ? 'client' : 'server',
        count: count,
        time: count > 0 ? Math.round(time / count) : 0,
        loadingSet: Date.now(),
        errorSet: Date.now()
      }
    });
    callback.outputs.map(function (_ref) {
      var id = _ref.id,
          property = _ref.property;
      var nodeId = recordNode(id, property);
      recordEdge(cb, nodeId, 'output');
    });
    callback.inputs.map(function (_ref2) {
      var id = _ref2.id,
          property = _ref2.property;
      var nodeId = recordNode(id, property);
      recordEdge(nodeId, cb, 'input');
    });
    callback.state.map(function (_ref3) {
      var id = _ref3.id,
          property = _ref3.property;
      var nodeId = recordNode(id, property);
      recordEdge(nodeId, cb, 'state');
    });
  }); // pull together props in the same component

  if (extraLinks) {
    (0, _ramda.values)(structure).forEach(function (childIds) {
      childIds.forEach(function (childFrom) {
        childIds.forEach(function (childTo) {
          if (childFrom !== childTo) {
            recordEdge(childFrom, childTo, 'hidden');
          }
        });
      });
    });
  }

  return elements;
}

function reduceStatus(status) {
  if ((0, _ramda.keys)(status).length === 2) {
    return status.latest;
  }

  return status;
}

function flattenOutputs(res) {
  var outputs = {};

  for (var idStr in res) {
    for (var prop in res[idStr]) {
      outputs[idStr + '.' + prop] = res[idStr][prop];
    }
  }

  return outputs;
}

function flattenInputs(inArray, _final) {
  (inArray || []).forEach(function (inItem) {
    if (Array.isArray(inItem)) {
      flattenInputs(inItem, _final);
    } else {
      var id = inItem.id,
          property = inItem.property,
          value = inItem.value;
      _final[(0, _dependencies.stringifyId)(id) + '.' + property] = value;
    }
  });
  return _final;
} // len('__dash_callback__.')


var cbPrefixLen = 18;
var dagreLayout = {
  name: 'dagre',
  padding: 10,
  ranker: 'tight-tree'
};
var forceLayout = {
  name: 'fcose',
  padding: 10,
  animate: false
};
var layouts = {
  'top-down': _objectSpread(_objectSpread({}, dagreLayout), {}, {
    spacingFactor: 0.8
  }),
  'left-right': _objectSpread(_objectSpread({}, dagreLayout), {}, {
    nodeSep: 0,
    rankSep: 80,
    rankDir: 'LR'
  }),
  force: forceLayout,
  'force-loose': forceLayout
};

function CallbackGraph() {
  // Grab items from the redux store.
  var paths = (0, _reactRedux.useSelector)(function (state) {
    return state.paths;
  });
  var layout = (0, _reactRedux.useSelector)(function (state) {
    return state.layout;
  });
  var graphs = (0, _reactRedux.useSelector)(function (state) {
    return state.graphs;
  });
  var profile = (0, _reactRedux.useSelector)(function (state) {
    return state.profile;
  });
  var changed = (0, _reactRedux.useSelector)(function (state) {
    return state.changed;
  });
  var lifecycleState = (0, _reactRedux.useSelector)(function (state) {
    return state.appLifecycle;
  }); // Keep track of cytoscape reference and user selected items.

  var _useState = (0, _react.useState)(null),
      _useState2 = _slicedToArray(_useState, 2),
      selected = _useState2[0],
      setSelected = _useState2[1];

  var _useState3 = (0, _react.useState)(null),
      _useState4 = _slicedToArray(_useState3, 2),
      cytoscape = _useState4[0],
      setCytoscape = _useState4[1];

  var graphLayout = profile.graphLayout;
  var chosenType = graphLayout === null || graphLayout === void 0 ? void 0 : graphLayout._chosenType;
  var layoutSelector = (0, _react.useRef)(null);

  var _useState5 = (0, _react.useState)(chosenType || 'top-down'),
      _useState6 = _slicedToArray(_useState5, 2),
      layoutType = _useState6[0],
      setLayoutType = _useState6[1]; // Generate and memoize the elements.


  var elements = (0, _react.useMemo)(function () {
    return generateElements(graphs, profile, layoutType === 'force');
  }, [graphs, layoutType]); // Custom hook to make sure cytoscape is loaded.

  var useCytoscapeEffect = function useCytoscapeEffect(effect, condition) {
    (0, _react.useEffect)(function () {
      return cytoscape && effect(cytoscape) || undefined;
    }, condition);
  };

  function setPresetLayout(_ref4) {
    var _layoutSelector$curre;

    var cy = _ref4.cy;
    var positions = {};
    cy.nodes().each(function (n) {
      positions[n.id()] = n.position();
    }); // Hack! We're mutating the redux store directly here, rather than
    // dispatching an action, because we don't want this to trigger a
    // rerender, we just want the layout to persist when the callback graph
    // is rerendered - either because there's new profile information to
    // display or because the graph was closed and reopened. The latter is
    // the reason we're not using component state to store the layout.

    profile.graphLayout = {
      name: 'preset',
      fit: false,
      positions: positions,
      zoom: cy.zoom(),
      pan: cy.pan(),
      _chosenType: (_layoutSelector$curre = layoutSelector.current) === null || _layoutSelector$curre === void 0 ? void 0 : _layoutSelector$curre.value
    };
  } // Adds callbacks once cyctoscape is intialized.


  useCytoscapeEffect(function (cy) {
    cytoscape.on('tap', 'node', function (e) {
      return setSelected(e.target);
    });
    cytoscape.on('tap', function (e) {
      if (e.target === cy) {
        setSelected(null);
      }
    });
    cytoscape.on('zoom', setPresetLayout);
    cytoscape.on('pan', setPresetLayout);
    cytoscape.nodes().on('position', setPresetLayout);
  }, [cytoscape]); // Set node classes on selected.

  useCytoscapeEffect(function (cy) {
    return selected && (0, _CallbackGraphEffects.updateSelectedNode)(cy, selected.data().id);
  }, [selected]); // Flash classes when props change. Uses changed as a trigger. Also
  // flash all input edges originating from this node and highlight
  // the subtree that contains the selected node.

  useCytoscapeEffect(function (cy) {
    return changed && (0, _CallbackGraphEffects.updateChangedProps)(cy, changed.id, changed.props);
  }, [changed]); // Update callbacks from profiling information.

  useCytoscapeEffect(function (cy) {
    return profile.updated.forEach(function (cb) {
      return (0, _CallbackGraphEffects.updateCallback)(cy, cb, profile.callbacks[cb]);
    });
  }, [profile.updated]);

  if (lifecycleState !== 'HYDRATED') {
    // If we get here too early - most likely during hot reloading - then
    // we need to bail out and wait for the full state to be available
    return /*#__PURE__*/_react["default"].createElement("div", {
      className: "dash-callback-dag--container"
    }, /*#__PURE__*/_react["default"].createElement("div", {
      className: "dash-callback-dag--message"
    }, /*#__PURE__*/_react["default"].createElement("div", null, "Waiting for app to be ready...")));
  } // FIXME: Move to a new component?
  // Generate the element introspection data.


  var elementName = '';
  var elementInfo = {};
  var hasPatterns = false;

  if (selected) {
    var getComponent = function getComponent(id) {
      // for now ignore pattern-matching IDs
      // to do better we may need to store the *actual* IDs used for each
      // callback invocation, since they need not match what's on the page now.
      if (id.charAt(0) === '{') {
        hasPatterns = true;
        return undefined;
      }

      var idPath = (0, _paths.getPath)(paths, id);
      return idPath ? (0, _ramda.path)(idPath, layout) : undefined;
    };

    var getPropValue = function getPropValue(data) {
      var parent = getComponent(data.parent);
      return parent ? parent.props[data.label] : undefined;
    };

    var data = selected.data();

    switch (data.type) {
      case 'component':
        {
          var _getComponent;

          var rest = (0, _ramda.omit)(['id'], (_getComponent = getComponent(data.id)) === null || _getComponent === void 0 ? void 0 : _getComponent.props);
          elementInfo = rest;
          elementName = data.id;
          break;
        }

      case 'property':
        {
          elementName = data.parent;
          elementInfo[data.label] = getPropValue(data);
          break;
        }
      // callback

      default:
        {
          elementInfo.type = data.mode; // Remove uid and set profile.

          var callbackOutputId = data.id.slice(cbPrefixLen);
          elementName = callbackOutputId.replace(/(^\.\.|\.\.$)/g, '');
          var cbProfile = profile.callbacks[callbackOutputId];

          if (cbProfile) {
            var count = cbProfile.count,
                status = cbProfile.status,
                network = cbProfile.network,
                resources = cbProfile.resources,
                total = cbProfile.total,
                compute = cbProfile.compute,
                result = cbProfile.result,
                inputs = cbProfile.inputs,
                state = cbProfile.state;

            var avg = function avg(v) {
              return Math.round(v / (count || 1));
            };

            elementInfo['call count'] = count;
            elementInfo.status = reduceStatus(status);
            var timing = elementInfo['time (avg milliseconds)'] = {
              total: avg(total),
              compute: avg(compute)
            };

            if (data.mode === 'server') {
              timing.network = avg(network.time);
              elementInfo['data transfer (avg bytes)'] = {
                download: avg(network.download),
                upload: avg(network.upload)
              };
            }

            for (var key in resources) {
              timing['user: ' + key] = avg(resources[key]);
            }

            elementInfo.outputs = flattenOutputs(result);
            elementInfo.inputs = flattenInputs(inputs, {});
            elementInfo.state = flattenInputs(state, {});
          } else {
            elementInfo['call count'] = 0;
          }
        }
    }
  }

  var cyLayout = chosenType === layoutType ? graphLayout : (0, _ramda.mergeRight)(layouts[layoutType], {
    ready: setPresetLayout
  });
  return /*#__PURE__*/_react["default"].createElement("div", {
    className: "dash-callback-dag--container"
  }, /*#__PURE__*/_react["default"].createElement(_reactCytoscapejs["default"], {
    style: {
      width: '100%',
      height: '100%'
    },
    cy: setCytoscape,
    elements: elements,
    layout: cyLayout,
    stylesheet: _CallbackGraphContainerStylesheet["default"]
  }), selected ? /*#__PURE__*/_react["default"].createElement("div", {
    className: "dash-callback-dag--info"
  }, hasPatterns ? /*#__PURE__*/_react["default"].createElement("div", null, "Info isn't supported for pattern-matching IDs at this time") : null, /*#__PURE__*/_react["default"].createElement(_reactJsonTree["default"], {
    data: elementInfo,
    theme: "summerfruit",
    labelRenderer: function labelRenderer(_keys) {
      return _keys.length === 1 ? elementName : _keys[0];
    },
    getItemString: function getItemString(type, data, itemType) {
      return /*#__PURE__*/_react["default"].createElement("span", null, itemType);
    },
    shouldExpandNode: function shouldExpandNode(keyName, data, level) {
      return level < 1;
    }
  })) : null, /*#__PURE__*/_react["default"].createElement("select", {
    className: "dash-callback-dag--layoutSelector",
    onChange: function onChange(e) {
      return setLayoutType(e.target.value);
    },
    value: layoutType,
    ref: layoutSelector
  }, (0, _ramda.keys)(layouts).map(function (k) {
    return /*#__PURE__*/_react["default"].createElement("option", {
      value: k,
      key: k
    }, k);
  })));
}

CallbackGraph.propTypes = {};

var UnconnectedCallbackGraphContainer = /*#__PURE__*/function (_Component) {
  _inherits(UnconnectedCallbackGraphContainer, _Component);

  var _super = _createSuper(UnconnectedCallbackGraphContainer);

  function UnconnectedCallbackGraphContainer(props) {
    var _this;

    _classCallCheck(this, UnconnectedCallbackGraphContainer);

    _this = _super.call(this, props);
    _this.state = {
      hasError: false
    };
    return _this;
  }

  _createClass(UnconnectedCallbackGraphContainer, [{
    key: "componentDidCatch",
    value: function componentDidCatch(error, info) {
      var dispatch = this.props.dispatch;
      dispatch((0, _actions.onError)({
        myID: this.state.myID,
        type: 'frontEnd',
        error: error,
        info: info
      }));
    }
  }, {
    key: "render",
    value: function render() {
      return this.state.hasError ? /*#__PURE__*/_react["default"].createElement("div", {
        className: "dash-callback-dag--container"
      }, /*#__PURE__*/_react["default"].createElement("div", {
        className: "dash-callback-dag--message"
      }, /*#__PURE__*/_react["default"].createElement("div", null, "Oops! The callback graph threw an error."), /*#__PURE__*/_react["default"].createElement("div", null, "Check the error list for details."))) : /*#__PURE__*/_react["default"].createElement(CallbackGraph, null);
    }
  }], [{
    key: "getDerivedStateFromError",
    value: function getDerivedStateFromError(_) {
      return {
        hasError: true
      };
    }
  }]);

  return UnconnectedCallbackGraphContainer;
}(_react.Component);

UnconnectedCallbackGraphContainer.propTypes = {
  dispatch: _propTypes["default"].func
};
var CallbackGraphContainer = (0, _reactRedux.connect)(null, function (dispatch) {
  return {
    dispatch: dispatch
  };
})(UnconnectedCallbackGraphContainer);
exports.CallbackGraphContainer = CallbackGraphContainer;