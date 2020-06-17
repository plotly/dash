"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.getLoadingState = getLoadingState;
exports.validateComponent = validateComponent;
exports.getLoadingHash = void 0;

var _ramda = require("ramda");

var _registry = _interopRequireDefault(require("../registry"));

var _dependencies = require("../actions/dependencies");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function isLoadingComponent(layout) {
  validateComponent(layout);
  return _registry["default"].resolve(layout)._dashprivate_isLoadingComponent;
}

var NULL_LOADING_STATE = false;

function getLoadingState(componentLayout, componentPath, loadingMap) {
  var _loadingFragment$__da;

  if (!loadingMap) {
    return NULL_LOADING_STATE;
  }

  var loadingFragment = (0, _ramda.path)(componentPath, loadingMap); // Component and children are not loading if there's no loading fragment
  // for the component's path in the layout.

  if (!loadingFragment) {
    return NULL_LOADING_STATE;
  }

  var idprop = loadingFragment.__dashprivate__idprop__;

  if (idprop) {
    return {
      is_loading: true,
      prop_name: idprop.property,
      component_name: (0, _dependencies.stringifyId)(idprop.id)
    };
  }

  var idprops = (_loadingFragment$__da = loadingFragment.__dashprivate__idprops__) === null || _loadingFragment$__da === void 0 ? void 0 : _loadingFragment$__da[0];

  if (idprops && isLoadingComponent(componentLayout)) {
    return {
      is_loading: true,
      prop_name: idprops.property,
      component_name: (0, _dependencies.stringifyId)(idprops.id)
    };
  }

  return NULL_LOADING_STATE;
}

var getLoadingHash = function getLoadingHash(componentPath, loadingMap) {
  var _ref, _ref2;

  return ((_ref = loadingMap && ((_ref2 = (0, _ramda.path)(componentPath, loadingMap)) === null || _ref2 === void 0 ? void 0 : _ref2.__dashprivate__idprops__)) !== null && _ref !== void 0 ? _ref : []).map(function (_ref3) {
    var id = _ref3.id,
        property = _ref3.property;
    return "".concat(id, ".").concat(property);
  }).join(',');
};

exports.getLoadingHash = getLoadingHash;

function validateComponent(componentDefinition) {
  if ((0, _ramda.type)(componentDefinition) === 'Array') {
    throw new Error('The children property of a component is a list of lists, instead ' + 'of just a list. ' + 'Check the component that has the following contents, ' + 'and remove one of the levels of nesting: \n' + JSON.stringify(componentDefinition, null, 2));
  }

  if ((0, _ramda.type)(componentDefinition) === 'Object' && !((0, _ramda.has)('namespace', componentDefinition) && (0, _ramda.has)('type', componentDefinition) && (0, _ramda.has)('props', componentDefinition))) {
    throw new Error('An object was provided as `children` instead of a component, ' + 'string, or number (or list of those). ' + 'Check the children property that looks something like:\n' + JSON.stringify(componentDefinition, null, 2));
  }
}