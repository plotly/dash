"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = exports.AugmentedTreeContainer = void 0;

var _react = _interopRequireWildcard(require("react"));

var _propTypes = _interopRequireDefault(require("prop-types"));

var _registry = _interopRequireDefault(require("./registry"));

var _exceptions = require("./exceptions");

var _reactRedux = require("react-redux");

var _ramda = require("ramda");

var _actions = require("./actions");

var _isSimpleComponent = _interopRequireDefault(require("./isSimpleComponent"));

var _persistence = require("./persistence");

var _ComponentErrorBoundary = _interopRequireDefault(require("./components/error/ComponentErrorBoundary.react"));

var _checkPropTypes = _interopRequireDefault(require("./checkPropTypes"));

var _dependencies = require("./actions/dependencies");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function _getRequireWildcardCache() { if (typeof WeakMap !== "function") return null; var cache = new WeakMap(); _getRequireWildcardCache = function _getRequireWildcardCache() { return cache; }; return cache; }

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } if (obj === null || _typeof(obj) !== "object" && typeof obj !== "function") { return { "default": obj }; } var cache = _getRequireWildcardCache(); if (cache && cache.has(obj)) { return cache.get(obj); } var newObj = {}; var hasPropertyDescriptor = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) { var desc = hasPropertyDescriptor ? Object.getOwnPropertyDescriptor(obj, key) : null; if (desc && (desc.get || desc.set)) { Object.defineProperty(newObj, key, desc); } else { newObj[key] = obj[key]; } } } newObj["default"] = obj; if (cache) { cache.set(obj, newObj); } return newObj; }

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } return _assertThisInitialized(self); }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance"); }

function _iterableToArray(iter) { if (Symbol.iterator in Object(iter) || Object.prototype.toString.call(iter) === "[object Arguments]") return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = new Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } }

function validateComponent(componentDefinition) {
  if ((0, _ramda.type)(componentDefinition) === 'Array') {
    throw new Error('The children property of a component is a list of lists, instead ' + 'of just a list. ' + 'Check the component that has the following contents, ' + 'and remove one of the levels of nesting: \n' + JSON.stringify(componentDefinition, null, 2));
  }

  if ((0, _ramda.type)(componentDefinition) === 'Object' && !((0, _ramda.has)('namespace', componentDefinition) && (0, _ramda.has)('type', componentDefinition) && (0, _ramda.has)('props', componentDefinition))) {
    throw new Error('An object was provided as `children` instead of a component, ' + 'string, or number (or list of those). ' + 'Check the children property that looks something like:\n' + JSON.stringify(componentDefinition, null, 2));
  }
}

var createContainer = function createContainer(component, path) {
  return (0, _isSimpleComponent["default"])(component) ? component : _react["default"].createElement(AugmentedTreeContainer, {
    key: component && component.props && (0, _dependencies.stringifyId)(component.props.id),
    _dashprivate_layout: component,
    _dashprivate_path: path
  });
};

function CheckedComponent(p) {
  var element = p.element,
      extraProps = p.extraProps,
      props = p.props,
      children = p.children,
      type = p.type;
  var errorMessage = (0, _checkPropTypes["default"])(element.propTypes, props, 'component prop', element);

  if (errorMessage) {
    (0, _exceptions.propTypeErrorHandler)(errorMessage, props, type);
  }

  return createElement(element, props, extraProps, children);
}

CheckedComponent.propTypes = {
  children: _propTypes["default"].any,
  element: _propTypes["default"].any,
  layout: _propTypes["default"].any,
  props: _propTypes["default"].any,
  extraProps: _propTypes["default"].any,
  id: _propTypes["default"].string
};

function createElement(element, props, extraProps, children) {
  var allProps = (0, _ramda.mergeRight)(props, extraProps);

  if (Array.isArray(children)) {
    return _react["default"].createElement.apply(_react["default"], [element, allProps].concat(_toConsumableArray(children)));
  }

  return _react["default"].createElement(element, allProps, children);
}

var TreeContainer = /*#__PURE__*/function (_Component) {
  _inherits(TreeContainer, _Component);

  function TreeContainer(props) {
    var _this;

    _classCallCheck(this, TreeContainer);

    _this = _possibleConstructorReturn(this, _getPrototypeOf(TreeContainer).call(this, props));
    _this.setProps = _this.setProps.bind(_assertThisInitialized(_this));
    return _this;
  }

  _createClass(TreeContainer, [{
    key: "setProps",
    value: function setProps(newProps) {
      var _this$props = this.props,
          _dashprivate_graphs = _this$props._dashprivate_graphs,
          _dashprivate_dispatch = _this$props._dashprivate_dispatch,
          _dashprivate_path = _this$props._dashprivate_path,
          _dashprivate_layout = _this$props._dashprivate_layout;
      var oldProps = this.getLayoutProps();
      var id = oldProps.id;
      var changedProps = (0, _ramda.pickBy)(function (val, key) {
        return !(0, _ramda.equals)(val, oldProps[key]);
      }, newProps);

      if (!(0, _ramda.isEmpty)(changedProps)) {
        // Identify the modified props that are required for callbacks
        var watchedKeys = (0, _dependencies.getWatchedKeys)(id, (0, _ramda.keys)(changedProps), _dashprivate_graphs); // setProps here is triggered by the UI - record these changes
        // for persistence

        (0, _persistence.recordUiEdit)(_dashprivate_layout, newProps, _dashprivate_dispatch); // Always update this component's props

        _dashprivate_dispatch((0, _actions.updateProps)({
          props: changedProps,
          itempath: _dashprivate_path
        })); // Only dispatch changes to Dash if a watched prop changed


        if (watchedKeys.length) {
          _dashprivate_dispatch((0, _actions.notifyObservers)({
            id: id,
            props: (0, _ramda.pick)(watchedKeys, changedProps)
          }));
        }
      }
    }
  }, {
    key: "getChildren",
    value: function getChildren(components, path) {
      if ((0, _ramda.isNil)(components)) {
        return null;
      }

      return Array.isArray(components) ? (0, _ramda.addIndex)(_ramda.map)(function (component, i) {
        return createContainer(component, (0, _ramda.concat)(path, ['props', 'children', i]));
      }, components) : createContainer(components, (0, _ramda.concat)(path, ['props', 'children']));
    }
  }, {
    key: "getComponent",
    value: function getComponent(_dashprivate_layout, children, loading_state, setProps) {
      var _dashprivate_config = this.props._dashprivate_config;

      if ((0, _ramda.isEmpty)(_dashprivate_layout)) {
        return null;
      }

      if ((0, _isSimpleComponent["default"])(_dashprivate_layout)) {
        return _dashprivate_layout;
      }

      validateComponent(_dashprivate_layout);

      var element = _registry["default"].resolve(_dashprivate_layout);

      var props = (0, _ramda.dissoc)('children', _dashprivate_layout.props);

      if ((0, _ramda.type)(props.id) === 'Object') {
        // Turn object ids (for wildcards) into unique strings.
        // Because of the `dissoc` above we're not mutating the layout,
        // just the id we pass on to the rendered component
        props.id = (0, _dependencies.stringifyId)(props.id);
      }

      var extraProps = {
        loading_state: loading_state,
        setProps: setProps
      };
      return _react["default"].createElement(_ComponentErrorBoundary["default"], {
        componentType: _dashprivate_layout.type,
        componentId: props.id,
        key: props.id
      }, _dashprivate_config.props_check ? _react["default"].createElement(CheckedComponent, {
        children: children,
        element: element,
        props: props,
        extraProps: extraProps,
        type: _dashprivate_layout.type
      }) : createElement(element, props, extraProps, children));
    }
  }, {
    key: "shouldComponentUpdate",
    value: function shouldComponentUpdate(nextProps) {
      var _dashprivate_layout = nextProps._dashprivate_layout,
          _dashprivate_loadingState = nextProps._dashprivate_loadingState;
      return _dashprivate_layout !== this.props._dashprivate_layout || _dashprivate_loadingState.is_loading !== this.props._dashprivate_loadingState.is_loading;
    }
  }, {
    key: "getLayoutProps",
    value: function getLayoutProps() {
      return (0, _ramda.propOr)({}, 'props', this.props._dashprivate_layout);
    }
  }, {
    key: "render",
    value: function render() {
      var _this$props2 = this.props,
          _dashprivate_layout = _this$props2._dashprivate_layout,
          _dashprivate_loadingState = _this$props2._dashprivate_loadingState,
          _dashprivate_path = _this$props2._dashprivate_path;
      var layoutProps = this.getLayoutProps();
      var children = this.getChildren(layoutProps.children, _dashprivate_path);
      return this.getComponent(_dashprivate_layout, children, _dashprivate_loadingState, this.setProps);
    }
  }]);

  return TreeContainer;
}(_react.Component);

TreeContainer.propTypes = {
  _dashprivate_graphs: _propTypes["default"].any,
  _dashprivate_dispatch: _propTypes["default"].func,
  _dashprivate_layout: _propTypes["default"].object,
  _dashprivate_loadingState: _propTypes["default"].object,
  _dashprivate_config: _propTypes["default"].object,
  _dashprivate_path: _propTypes["default"].array
};

function isLoadingComponent(layout) {
  validateComponent(layout);
  return _registry["default"].resolve(layout)._dashprivate_isLoadingComponent;
}

function getNestedIds(layout) {
  var ids = [];
  var queue = [layout];

  while (queue.length) {
    var elementLayout = queue.shift();
    var props = elementLayout && elementLayout.props;

    if (!props) {
      continue;
    }

    var children = props.children,
        id = props.id;

    if (id) {
      ids.push(id);
    }

    if (children) {
      var filteredChildren = (0, _ramda.filter)(function (child) {
        return !(0, _isSimpleComponent["default"])(child) && !isLoadingComponent(child);
      }, Array.isArray(children) ? children : [children]);
      queue.push.apply(queue, _toConsumableArray(filteredChildren));
    }
  }

  return ids;
}

function getLoadingState(layout, pendingCallbacks) {
  var ids = isLoadingComponent(layout) ? getNestedIds(layout) : layout && layout.props.id && [layout.props.id];
  var isLoading = false;
  var loadingProp;
  var loadingComponent;

  if (pendingCallbacks && pendingCallbacks.length && ids && ids.length) {
    var idStrs = ids.map(_dependencies.stringifyId);
    pendingCallbacks.forEach(function (cb) {
      var requestId = cb.requestId,
          requestedOutputs = cb.requestedOutputs;

      if (requestId === undefined) {
        return;
      }

      idStrs.forEach(function (idStr) {
        var props = requestedOutputs[idStr];

        if (props) {
          isLoading = true; // TODO: what about multiple loading components / props?

          loadingComponent = idStr;
          loadingProp = props[0];
        }
      });
    });
  } // Set loading state


  return {
    is_loading: isLoading,
    prop_name: loadingProp,
    component_name: loadingComponent
  };
}

var AugmentedTreeContainer = (0, _reactRedux.connect)(function (state) {
  return {
    graphs: state.graphs,
    pendingCallbacks: state.pendingCallbacks,
    config: state.config
  };
}, function (dispatch) {
  return {
    dispatch: dispatch
  };
}, function (stateProps, dispatchProps, ownProps) {
  return {
    _dashprivate_graphs: stateProps.graphs,
    _dashprivate_dispatch: dispatchProps.dispatch,
    _dashprivate_layout: ownProps._dashprivate_layout,
    _dashprivate_path: ownProps._dashprivate_path,
    _dashprivate_loadingState: getLoadingState(ownProps._dashprivate_layout, stateProps.pendingCallbacks),
    _dashprivate_config: stateProps.config
  };
})(TreeContainer);
exports.AugmentedTreeContainer = AugmentedTreeContainer;
var _default = AugmentedTreeContainer;
exports["default"] = _default;