"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;
var _default = {
  resolve: function resolve(component) {
    var type = component.type,
        namespace = component.namespace;
    var ns = window[namespace];

    if (ns) {
      if (ns[type]) {
        return ns[type];
      }

      throw new Error("Component ".concat(type, " not found in ").concat(namespace));
    }

    throw new Error("".concat(namespace, " was not found."));
  }
};
exports["default"] = _default;