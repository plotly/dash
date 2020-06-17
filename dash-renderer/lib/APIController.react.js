"use strict";

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = exports.DashContext = void 0;

var _reactRedux = require("react-redux");

var _ramda = require("ramda");

var _react = _interopRequireWildcard(require("react"));

var _propTypes = _interopRequireDefault(require("prop-types"));

var _TreeContainer = _interopRequireDefault(require("./TreeContainer"));

var _GlobalErrorContainer = _interopRequireDefault(require("./components/error/GlobalErrorContainer.react"));

var _actions = require("./actions");

var _paths = require("./actions/paths");

var _dependencies = require("./actions/dependencies");

var _api = _interopRequireDefault(require("./actions/api"));

var _utils = require("./actions/utils");

var _persistence = require("./persistence");

var _constants = require("./reducers/constants");

var _constants2 = require("./constants/constants");

var _TreeContainer2 = require("./utils/TreeContainer");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function _getRequireWildcardCache() { if (typeof WeakMap !== "function") return null; var cache = new WeakMap(); _getRequireWildcardCache = function _getRequireWildcardCache() { return cache; }; return cache; }

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } if (obj === null || _typeof(obj) !== "object" && typeof obj !== "function") { return { "default": obj }; } var cache = _getRequireWildcardCache(); if (cache && cache.has(obj)) { return cache.get(obj); } var newObj = {}; var hasPropertyDescriptor = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) { var desc = hasPropertyDescriptor ? Object.getOwnPropertyDescriptor(obj, key) : null; if (desc && (desc.get || desc.set)) { Object.defineProperty(newObj, key, desc); } else { newObj[key] = obj[key]; } } } newObj["default"] = obj; if (cache) { cache.set(obj, newObj); } return newObj; }

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance"); }

function _iterableToArrayLimit(arr, i) { if (!(Symbol.iterator in Object(arr) || Object.prototype.toString.call(arr) === "[object Arguments]")) { return; } var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

var DashContext = (0, _react.createContext)({});
/**
 * Fire off API calls for initialization
 * @param {*} props props
 * @returns {*} component
 */

exports.DashContext = DashContext;

var UnconnectedContainer = function UnconnectedContainer(props) {
  var appLifecycle = props.appLifecycle,
      config = props.config,
      dependenciesRequest = props.dependenciesRequest,
      error = props.error,
      layoutRequest = props.layoutRequest,
      layout = props.layout,
      loadingMap = props.loadingMap;

  var _useState = (0, _react.useState)(false),
      _useState2 = _slicedToArray(_useState, 2),
      errorLoading = _useState2[0],
      setErrorLoading = _useState2[1];

  var events = (0, _react.useRef)(null);

  if (!events.current) {
    events.current = new _utils.EventEmitter();
  }

  var renderedTree = (0, _react.useRef)(false);
  var propsRef = (0, _react.useRef)({});
  propsRef.current = props;
  var provider = (0, _react.useRef)({
    fn: function fn() {
      return {
        _dashprivate_config: propsRef.current.config,
        _dashprivate_dispatch: propsRef.current.dispatch,
        _dashprivate_graphs: propsRef.current.graphs,
        _dashprivate_loadingMap: propsRef.current.loadingMap
      };
    }
  });
  (0, _react.useEffect)(storeEffect.bind(null, props, events, setErrorLoading));
  (0, _react.useEffect)(function () {
    if (renderedTree.current) {
      renderedTree.current = false;
      events.current.emit('rendered');
    }
  });
  var content;

  if (layoutRequest.status && !(0, _ramda.includes)(layoutRequest.status, [_constants2.STATUS.OK, 'loading'])) {
    content = _react["default"].createElement("div", {
      className: "_dash-error"
    }, "Error loading layout");
  } else if (errorLoading || dependenciesRequest.status && !(0, _ramda.includes)(dependenciesRequest.status, [_constants2.STATUS.OK, 'loading'])) {
    content = _react["default"].createElement("div", {
      className: "_dash-error"
    }, "Error loading dependencies");
  } else if (appLifecycle === (0, _constants.getAppState)('HYDRATED')) {
    renderedTree.current = true;
    content = _react["default"].createElement(DashContext.Provider, {
      value: provider.current
    }, _react["default"].createElement(_TreeContainer["default"], {
      _dashprivate_error: error,
      _dashprivate_layout: layout,
      _dashprivate_loadingState: (0, _TreeContainer2.getLoadingState)(layout, [], loadingMap),
      _dashprivate_loadingStateHash: (0, _TreeContainer2.getLoadingHash)([], loadingMap),
      _dashprivate_path: JSON.stringify([])
    }));
  } else {
    content = _react["default"].createElement("div", {
      className: "_dash-loading"
    }, "Loading...");
  }

  return config && config.ui === true ? _react["default"].createElement(_GlobalErrorContainer["default"], null, content) : content;
};

function storeEffect(props, events, setErrorLoading) {
  var appLifecycle = props.appLifecycle,
      dependenciesRequest = props.dependenciesRequest,
      dispatch = props.dispatch,
      error = props.error,
      graphs = props.graphs,
      layout = props.layout,
      layoutRequest = props.layoutRequest;

  if ((0, _ramda.isEmpty)(layoutRequest)) {
    dispatch((0, _api["default"])('_dash-layout', 'GET', 'layoutRequest'));
  } else if (layoutRequest.status === _constants2.STATUS.OK) {
    if ((0, _ramda.isEmpty)(layout)) {
      var finalLayout = (0, _persistence.applyPersistence)(layoutRequest.content, dispatch);
      dispatch((0, _actions.setPaths)((0, _paths.computePaths)(finalLayout, [], null, events.current)));
      dispatch((0, _actions.setLayout)(finalLayout));
    }
  }

  if ((0, _ramda.isEmpty)(dependenciesRequest)) {
    dispatch((0, _api["default"])('_dash-dependencies', 'GET', 'dependenciesRequest'));
  } else if (dependenciesRequest.status === _constants2.STATUS.OK && (0, _ramda.isEmpty)(graphs)) {
    dispatch((0, _actions.setGraphs)((0, _dependencies.computeGraphs)(dependenciesRequest.content, (0, _actions.dispatchError)(dispatch))));
  }

  if ( // dependenciesRequest and its computed stores
  dependenciesRequest.status === _constants2.STATUS.OK && !(0, _ramda.isEmpty)(graphs) && // LayoutRequest and its computed stores
  layoutRequest.status === _constants2.STATUS.OK && !(0, _ramda.isEmpty)(layout) && // Hasn't already hydrated
  appLifecycle === (0, _constants.getAppState)('STARTED')) {
    var hasError = false;

    try {
      dispatch((0, _actions.hydrateInitialOutputs)((0, _actions.dispatchError)(dispatch)));
    } catch (err) {
      // Display this error in devtools, unless we have errors
      // already, in which case we assume this new one is moot
      if (!error.frontEnd.length && !error.backEnd.length) {
        dispatch((0, _actions.onError)({
          type: 'backEnd',
          error: err
        }));
      }

      hasError = true;
    } finally {
      setErrorLoading(hasError);
    }
  }
}

UnconnectedContainer.propTypes = {
  appLifecycle: _propTypes["default"].oneOf([(0, _constants.getAppState)('STARTED'), (0, _constants.getAppState)('HYDRATED')]),
  dispatch: _propTypes["default"].func,
  dependenciesRequest: _propTypes["default"].object,
  graphs: _propTypes["default"].object,
  layoutRequest: _propTypes["default"].object,
  layout: _propTypes["default"].object,
  loadingMap: _propTypes["default"].any,
  history: _propTypes["default"].any,
  error: _propTypes["default"].object,
  config: _propTypes["default"].object
};
var Container = (0, _reactRedux.connect)( // map state to props
function (state) {
  return {
    appLifecycle: state.appLifecycle,
    dependenciesRequest: state.dependenciesRequest,
    layoutRequest: state.layoutRequest,
    layout: state.layout,
    loadingMap: state.loadingMap,
    graphs: state.graphs,
    history: state.history,
    error: state.error,
    config: state.config
  };
}, function (dispatch) {
  return {
    dispatch: dispatch
  };
})(UnconnectedContainer);
var _default = Container;
exports["default"] = _default;