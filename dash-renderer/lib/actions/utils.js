"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.urlBase = urlBase;
exports.EventEmitter = exports.crawlLayout = void 0;

var _ramda = require("ramda");

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

/*
 * requests_pathname_prefix is the new config parameter introduced in
 * dash==0.18.0. The previous versions just had url_base_pathname
 */
function urlBase(config) {
  var hasUrlBase = (0, _ramda.has)('url_base_pathname', config);
  var hasReqPrefix = (0, _ramda.has)('requests_pathname_prefix', config);

  if ((0, _ramda.type)(config) !== 'Object' || !hasUrlBase && !hasReqPrefix) {
    throw new Error("\n            Trying to make an API request but neither\n            \"url_base_pathname\" nor \"requests_pathname_prefix\"\n            is in `config`. `config` is: ", config);
  }

  var base = hasReqPrefix ? config.requests_pathname_prefix : config.url_base_pathname;
  return base.charAt(base.length - 1) === '/' ? base : base + '/';
}

var propsChildren = ['props', 'children']; // crawl a layout object or children array, apply a function on every object

var crawlLayout = function crawlLayout(object, func) {
  var currentPath = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : [];

  if (Array.isArray(object)) {
    // children array
    object.forEach(function (child, i) {
      crawlLayout(child, func, (0, _ramda.append)(i, currentPath));
    });
  } else if ((0, _ramda.type)(object) === 'Object') {
    func(object, currentPath);
    var children = (0, _ramda.path)(propsChildren, object);

    if (children) {
      var newPath = (0, _ramda.concat)(currentPath, propsChildren);
      crawlLayout(children, func, newPath);
    }
  }
}; // There are packages for this but it's simple enough, I just
// adapted it from https://gist.github.com/mudge/5830382


exports.crawlLayout = crawlLayout;

var EventEmitter = /*#__PURE__*/function () {
  function EventEmitter() {
    _classCallCheck(this, EventEmitter);

    this._ev = {};
  }

  _createClass(EventEmitter, [{
    key: "on",
    value: function on(event, listener) {
      var _this = this;

      var events = this._ev[event] = this._ev[event] || [];
      events.push(listener);
      return function () {
        return _this.removeListener(event, listener);
      };
    }
  }, {
    key: "removeListener",
    value: function removeListener(event, listener) {
      var events = this._ev[event];

      if (events) {
        var idx = events.indexOf(listener);

        if (idx > -1) {
          events.splice(idx, 1);
        }
      }
    }
  }, {
    key: "emit",
    value: function emit(event) {
      var _this2 = this;

      for (var _len = arguments.length, args = new Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {
        args[_key - 1] = arguments[_key];
      }

      var events = this._ev[event];

      if (events) {
        events.forEach(function (listener) {
          return listener.apply(_this2, args);
        });
      }
    }
  }, {
    key: "once",
    value: function once(event, listener) {
      var _this3 = this;

      var remove = this.on(event, function () {
        remove();

        for (var _len2 = arguments.length, args = new Array(_len2), _key2 = 0; _key2 < _len2; _key2++) {
          args[_key2] = arguments[_key2];
        }

        listener.apply(_this3, args);
      });
    }
  }]);

  return EventEmitter;
}();

exports.EventEmitter = EventEmitter;