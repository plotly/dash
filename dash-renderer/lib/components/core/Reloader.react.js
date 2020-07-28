"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var _ramda = require("ramda");

var _react = _interopRequireDefault(require("react"));

var _propTypes = _interopRequireDefault(require("prop-types"));

var _reactRedux = require("react-redux");

var _api = _interopRequireDefault(require("../../actions/api"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _createForOfIteratorHelper(o, allowArrayLike) { var it; if (typeof Symbol === "undefined" || o[Symbol.iterator] == null) { if (Array.isArray(o) || (it = _unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e) { throw _e; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = o[Symbol.iterator](); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e2) { didErr = true; err = _e2; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

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

var Reloader = /*#__PURE__*/function (_React$Component) {
  _inherits(Reloader, _React$Component);

  var _super = _createSuper(Reloader);

  function Reloader(props) {
    var _this;

    _classCallCheck(this, Reloader);

    _this = _super.call(this, props);

    if (props.config.hot_reload) {
      var _props$config$hot_rel = props.config.hot_reload,
          interval = _props$config$hot_rel.interval,
          max_retry = _props$config$hot_rel.max_retry;
      _this.state = {
        interval: interval,
        disabled: false,
        intervalId: null,
        packages: null,
        max_retry: max_retry
      };
    } else {
      _this.state = {
        disabled: true
      };
    }

    _this._retry = 0;
    _this._head = document.querySelector('head');
    _this.clearInterval = _this.clearInterval.bind(_assertThisInitialized(_this));
    return _this;
  }

  _createClass(Reloader, [{
    key: "clearInterval",
    value: function clearInterval() {
      window.clearInterval(this.state.intervalId);
      this.setState({
        intervalId: null
      });
    }
  }, {
    key: "componentDidUpdate",
    value: function componentDidUpdate(prevProps, prevState) {
      var reloadRequest = this.state.reloadRequest;
      var dispatch = this.props.dispatch; // In the beginning, reloadRequest won't be defined

      if (!reloadRequest) {
        return;
      }
      /*
       * When reloadRequest is first defined, prevState won't be defined
       * for one render loop.
       * The first reloadRequest defines the initial/baseline hash -
       * it doesn't require a reload
       */


      if (!(0, _ramda.has)('reloadRequest', prevState)) {
        return;
      }

      if (reloadRequest.status === 200 && (0, _ramda.path)(['content', 'reloadHash'], reloadRequest) !== (0, _ramda.path)(['reloadRequest', 'content', 'reloadHash'], prevState)) {
        // Check for CSS (!content.hard) or new package assets
        if (reloadRequest.content.hard || !(0, _ramda.equals)(reloadRequest.content.packages.length, (0, _ramda.pathOr)([], ['reloadRequest', 'content', 'packages'], prevState).length) || !(0, _ramda.equals)((0, _ramda.sort)((0, _ramda.comparator)(_ramda.lt), reloadRequest.content.packages), (0, _ramda.sort)((0, _ramda.comparator)(_ramda.lt), (0, _ramda.pathOr)([], ['reloadRequest', 'content', 'packages'], prevState)))) {
          // Look if it was a css file.
          var was_css = false; // eslint-disable-next-line prefer-const

          var _iterator = _createForOfIteratorHelper(reloadRequest.content.files),
              _step;

          try {
            for (_iterator.s(); !(_step = _iterator.n()).done;) {
              var a = _step.value;

              if (a.is_css) {
                was_css = true;
                var nodesToDisable = []; // Search for the old file by xpath.

                var it = document.evaluate("//link[contains(@href, \"".concat(a.url, "\")]"), this._head);
                var node = it.iterateNext();

                while (node) {
                  nodesToDisable.push(node);
                  node = it.iterateNext();
                }

                (0, _ramda.forEach)(function (n) {
                  return n.setAttribute('disabled', 'disabled');
                }, nodesToDisable);

                if (a.modified > 0) {
                  var link = document.createElement('link');
                  link.href = "".concat(a.url, "?m=").concat(a.modified);
                  link.type = 'text/css';
                  link.rel = 'stylesheet';

                  this._head.appendChild(link); // Else the file was deleted.

                }
              } else {
                // If there's another kind of file here do a hard reload.
                was_css = false;
                break;
              }
            }
          } catch (err) {
            _iterator.e(err);
          } finally {
            _iterator.f();
          }

          if (!was_css) {
            // Assets file have changed
            // or a component lib has been added/removed -
            // Must do a hard reload
            window.location.reload();
          }
        } else {
          // Backend code changed - can do a soft reload in place
          dispatch({
            type: 'RELOAD'
          });
        }
      } else if (reloadRequest.status === 500) {
        if (this._retry > this.state.max_retry) {
          this.clearInterval(); // Integrate with dev tools ui?!

          window.alert("\n                    Reloader failed after ".concat(this._retry, " times.\n                    Please check your application for errors.\n                    "));
        }

        this._retry++;
      }
    }
  }, {
    key: "componentDidMount",
    value: function componentDidMount() {
      var _this$props = this.props,
          dispatch = _this$props.dispatch,
          reloadRequest = _this$props.reloadRequest;
      var _this$state = this.state,
          disabled = _this$state.disabled,
          interval = _this$state.interval;

      if (!disabled && !this.state.intervalId) {
        var intervalId = window.setInterval(function () {
          // Prevent requests from piling up - reloading can take
          // many seconds (10-30) and the interval is 3s by default
          if (reloadRequest.status !== 'loading') {
            dispatch((0, _api["default"])('_reload-hash', 'GET', 'reloadRequest'));
          }
        }, interval);
        this.setState({
          intervalId: intervalId
        });
      }
    }
  }, {
    key: "componentWillUnmount",
    value: function componentWillUnmount() {
      if (!this.state.disabled && this.state.intervalId) {
        this.clearInterval();
      }
    }
  }, {
    key: "render",
    value: function render() {
      return null;
    }
  }], [{
    key: "getDerivedStateFromProps",
    value: function getDerivedStateFromProps(props) {
      /*
       * Save the non-loading requests in the state in order to compare
       * current hashes with previous hashes.
       * Note that if there wasn't a "loading" state for the requests,
       * then we  could simply compare `props` with `prevProps` in
       * `componentDidUpdate`.
       */
      if (!(0, _ramda.isEmpty)(props.reloadRequest) && props.reloadRequest.status !== 'loading') {
        return {
          reloadRequest: props.reloadRequest
        };
      }

      return null;
    }
  }]);

  return Reloader;
}(_react["default"].Component);

Reloader.defaultProps = {};
Reloader.propTypes = {
  id: _propTypes["default"].string,
  config: _propTypes["default"].object,
  reloadRequest: _propTypes["default"].object,
  dispatch: _propTypes["default"].func,
  interval: _propTypes["default"].number
};

var _default = (0, _reactRedux.connect)(function (state) {
  return {
    config: state.config,
    reloadRequest: state.reloadRequest
  };
}, function (dispatch) {
  return {
    dispatch: dispatch
  };
})(Reloader);

exports["default"] = _default;