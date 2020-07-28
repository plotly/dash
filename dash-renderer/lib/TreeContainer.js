"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _react = _interopRequireWildcard(require("react"));

var _propTypes = _interopRequireDefault(require("prop-types"));

var _registry = _interopRequireDefault(require("./registry"));

var _exceptions = require("./exceptions");

var _ramda = require("ramda");

var _actions = require("./actions");

var _isSimpleComponent = _interopRequireDefault(require("./isSimpleComponent"));

var _persistence = require("./persistence");

var _ComponentErrorBoundary = _interopRequireDefault(require("./components/error/ComponentErrorBoundary.react"));

var _checkPropTypes = _interopRequireDefault(require("./checkPropTypes"));

var _dependencies = require("./actions/dependencies");

var _TreeContainer = require("./utils/TreeContainer");

var _APIController = require("./APIController.react");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function _getRequireWildcardCache() { if (typeof WeakMap !== "function") return null; var cache = new WeakMap(); _getRequireWildcardCache = function _getRequireWildcardCache() { return cache; }; return cache; }

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } if (obj === null || _typeof(obj) !== "object" && typeof obj !== "function") { return { "default": obj }; } var cache = _getRequireWildcardCache(); if (cache && cache.has(obj)) { return cache.get(obj); } var newObj = {}; var hasPropertyDescriptor = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) { var desc = hasPropertyDescriptor ? Object.getOwnPropertyDescriptor(obj, key) : null; if (desc && (desc.get || desc.set)) { Object.defineProperty(newObj, key, desc); } else { newObj[key] = obj[key]; } } } newObj["default"] = obj; if (cache) { cache.set(obj, newObj); } return newObj; }

function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { _defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

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

function _extends() { _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; }; return _extends.apply(this, arguments); }

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) return _arrayLikeToArray(arr); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

var NOT_LOADING = {
  is_loading: false
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
    return /*#__PURE__*/_react["default"].createElement.apply(_react["default"], [element, allProps].concat(_toConsumableArray(children)));
  }

  return /*#__PURE__*/_react["default"].createElement(element, allProps, children);
}

var TreeContainer = /*#__PURE__*/(0, _react.memo)(function (props) {
  return /*#__PURE__*/_react["default"].createElement(_APIController.DashContext.Consumer, null, function (context) {
    return /*#__PURE__*/_react["default"].createElement(BaseTreeContainer, _extends({}, context.fn(), props, {
      _dashprivate_path: JSON.parse(props._dashprivate_path)
    }));
  });
});

var BaseTreeContainer = /*#__PURE__*/function (_Component) {
  _inherits(BaseTreeContainer, _Component);

  var _super = _createSuper(BaseTreeContainer);

  function BaseTreeContainer(props) {
    var _this;

    _classCallCheck(this, BaseTreeContainer);

    _this = _super.call(this, props);
    _this.setProps = _this.setProps.bind(_assertThisInitialized(_this));
    return _this;
  }

  _createClass(BaseTreeContainer, [{
    key: "createContainer",
    value: function createContainer(props, component, path) {
      return (0, _isSimpleComponent["default"])(component) ? component : /*#__PURE__*/_react["default"].createElement(TreeContainer, {
        key: component && component.props && (0, _dependencies.stringifyId)(component.props.id),
        _dashprivate_error: props._dashprivate_error,
        _dashprivate_layout: component,
        _dashprivate_loadingState: (0, _TreeContainer.getLoadingState)(component, path, props._dashprivate_loadingMap),
        _dashprivate_loadingStateHash: (0, _TreeContainer.getLoadingHash)(path, props._dashprivate_loadingMap),
        _dashprivate_path: JSON.stringify(path)
      });
    }
  }, {
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
      var _this2 = this;

      if ((0, _ramda.isNil)(components)) {
        return null;
      }

      return Array.isArray(components) ? (0, _ramda.addIndex)(_ramda.map)(function (component, i) {
        return _this2.createContainer(_this2.props, component, (0, _ramda.concat)(path, ['props', 'children', i]));
      }, components) : this.createContainer(this.props, components, (0, _ramda.concat)(path, ['props', 'children']));
    }
  }, {
    key: "getComponent",
    value: function getComponent(_dashprivate_layout, children, loading_state, setProps) {
      var _this$props2 = this.props,
          _dashprivate_config = _this$props2._dashprivate_config,
          _dashprivate_dispatch = _this$props2._dashprivate_dispatch,
          _dashprivate_error = _this$props2._dashprivate_error;

      if ((0, _ramda.isEmpty)(_dashprivate_layout)) {
        return null;
      }

      if ((0, _isSimpleComponent["default"])(_dashprivate_layout)) {
        return _dashprivate_layout;
      }

      (0, _TreeContainer.validateComponent)(_dashprivate_layout);

      var element = _registry["default"].resolve(_dashprivate_layout);

      var props = (0, _ramda.dissoc)('children', _dashprivate_layout.props);

      if ((0, _ramda.type)(props.id) === 'Object') {
        // Turn object ids (for wildcards) into unique strings.
        // Because of the `dissoc` above we're not mutating the layout,
        // just the id we pass on to the rendered component
        props.id = (0, _dependencies.stringifyId)(props.id);
      }

      var extraProps = {
        loading_state: loading_state || NOT_LOADING,
        setProps: setProps
      };
      return /*#__PURE__*/_react["default"].createElement(_ComponentErrorBoundary["default"], {
        componentType: _dashprivate_layout.type,
        componentId: props.id,
        key: props.id,
        dispatch: _dashprivate_dispatch,
        error: _dashprivate_error
      }, _dashprivate_config.props_check ? /*#__PURE__*/_react["default"].createElement(CheckedComponent, {
        children: children,
        element: element,
        props: props,
        extraProps: extraProps,
        type: _dashprivate_layout.type
      }) : createElement(element, props, extraProps, children));
    }
  }, {
    key: "getLayoutProps",
    value: function getLayoutProps() {
      return (0, _ramda.propOr)({}, 'props', this.props._dashprivate_layout);
    }
  }, {
    key: "render",
    value: function render() {
      var _this$props3 = this.props,
          _dashprivate_layout = _this$props3._dashprivate_layout,
          _dashprivate_loadingState = _this$props3._dashprivate_loadingState,
          _dashprivate_path = _this$props3._dashprivate_path;
      var layoutProps = this.getLayoutProps();
      var children = this.getChildren(layoutProps.children, _dashprivate_path);
      return this.getComponent(_dashprivate_layout, children, _dashprivate_loadingState, this.setProps);
    }
  }]);

  return BaseTreeContainer;
}(_react.Component);

TreeContainer.propTypes = {
  _dashprivate_error: _propTypes["default"].any,
  _dashprivate_layout: _propTypes["default"].object,
  _dashprivate_loadingState: _propTypes["default"].oneOfType([_propTypes["default"].object, _propTypes["default"].bool]),
  _dashprivate_loadingStateHash: _propTypes["default"].string,
  _dashprivate_path: _propTypes["default"].string
};
BaseTreeContainer.propTypes = _objectSpread(_objectSpread({}, TreeContainer.propTypes), {}, {
  _dashprivate_config: _propTypes["default"].object,
  _dashprivate_dispatch: _propTypes["default"].func,
  _dashprivate_graphs: _propTypes["default"].any,
  _dashprivate_loadingMap: _propTypes["default"].any,
  _dashprivate_path: _propTypes["default"].array
});
var _default = TreeContainer;
exports["default"] = _default;