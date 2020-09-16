"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.recordUiEdit = recordUiEdit;
exports.applyPersistence = applyPersistence;
exports.prunePersistence = prunePersistence;
exports.stores = exports.storePrefix = void 0;

var _ramda = require("ramda");

var _reduxActions = require("redux-actions");

var _registry = _interopRequireDefault(require("./registry"));

var _dependencies = require("./actions/dependencies");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _unsupportedIterableToArray(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _iterableToArrayLimit(arr, i) { if (typeof Symbol === "undefined" || !(Symbol.iterator in Object(arr))) return; var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

var storePrefix = '_dash_persistence.';
exports.storePrefix = storePrefix;

function err(e) {
  var error = typeof e === 'string' ? new Error(e) : e;
  return (0, _reduxActions.createAction)('ON_ERROR')({
    type: 'frontEnd',
    error: error
  });
}
/*
 * Does a key fit this prefix? Must either be an exact match
 * or, if a separator is provided, a scoped match - exact prefix
 * followed by the separator (then anything else)
 */


function keyPrefixMatch(prefix, separator) {
  var fullStr = prefix + separator;
  var fullLen = fullStr.length;
  return function (key) {
    return key === prefix || key.substr(0, fullLen) === fullStr;
  };
}

var UNDEFINED = 'U';

var _parse = function _parse(val) {
  return val === UNDEFINED ? undefined : JSON.parse(val || null);
};

var _stringify = function _stringify(val) {
  return val === undefined ? UNDEFINED : JSON.stringify(val);
};

var WebStore = /*#__PURE__*/function () {
  function WebStore(backEnd) {
    _classCallCheck(this, WebStore);

    this._name = backEnd;
    this._storage = window[backEnd];
  }

  _createClass(WebStore, [{
    key: "hasItem",
    value: function hasItem(key) {
      return this._storage.getItem(storePrefix + key) !== null;
    }
  }, {
    key: "getItem",
    value: function getItem(key) {
      // note: _storage.getItem returns null on missing keys
      // and JSON.parse(null) returns null as well
      return _parse(this._storage.getItem(storePrefix + key));
    }
  }, {
    key: "_setItem",
    value: function _setItem(key, value) {
      // unprotected version of setItem, for use by tryGetWebStore
      this._storage.setItem(storePrefix + key, _stringify(value));
    }
    /*
     * In addition to the regular key->value to set, setItem takes
     * dispatch as a parameter, so it can report OOM to devtools
     */

  }, {
    key: "setItem",
    value: function setItem(key, value, dispatch) {
      try {
        this._setItem(key, value);
      } catch (e) {
        dispatch(err("".concat(key, " failed to save in ").concat(this._name, ". Persisted props may be lost."))); // TODO: at some point we may want to convert this to fall back
        // on memory, pulling out all persistence keys and putting them
        // in a MemStore that gets used from then onward.
      }
    }
  }, {
    key: "removeItem",
    value: function removeItem(key) {
      this._storage.removeItem(storePrefix + key);
    }
    /*
     * clear matching keys matching (optionally followed by a dot and more
     * characters) - or all keys associated with this store if no prefix.
     */

  }, {
    key: "clear",
    value: function clear(keyPrefix) {
      var _this = this;

      var fullPrefix = storePrefix + (keyPrefix || '');
      var keyMatch = keyPrefixMatch(fullPrefix, keyPrefix ? '.' : '');
      var keysToRemove = []; // 2-step process, so we don't depend on any particular behavior of
      // key order while removing some

      for (var i = 0; i < this._storage.length; i++) {
        var fullKey = this._storage.key(i);

        if (keyMatch(fullKey)) {
          keysToRemove.push(fullKey);
        }
      }

      (0, _ramda.forEach)(function (k) {
        return _this._storage.removeItem(k);
      }, keysToRemove);
    }
  }]);

  return WebStore;
}();

var MemStore = /*#__PURE__*/function () {
  function MemStore() {
    _classCallCheck(this, MemStore);

    this._data = {};
  }

  _createClass(MemStore, [{
    key: "hasItem",
    value: function hasItem(key) {
      return key in this._data;
    }
  }, {
    key: "getItem",
    value: function getItem(key) {
      // run this storage through JSON too so we know we get a fresh object
      // each retrieval
      return _parse(this._data[key]);
    }
  }, {
    key: "setItem",
    value: function setItem(key, value) {
      this._data[key] = _stringify(value);
    }
  }, {
    key: "removeItem",
    value: function removeItem(key) {
      delete this._data[key];
    }
  }, {
    key: "clear",
    value: function clear(keyPrefix) {
      var _this2 = this;

      if (keyPrefix) {
        (0, _ramda.forEach)(function (key) {
          return delete _this2._data[key];
        }, (0, _ramda.filter)(keyPrefixMatch(keyPrefix, '.'), (0, _ramda.keys)(this._data)));
      } else {
        this._data = {};
      }
    }
  }]);

  return MemStore;
}(); // Make a string 2^16 characters long (*2 bytes/char = 130kB), to test storage.
// That should be plenty for common persistence use cases,
// without getting anywhere near typical browser limits


var pow = 16;

function longString() {
  var s = 'Spam';

  for (var i = 2; i < pow; i++) {
    s += s;
  }

  return s;
}

var stores = {
  memory: new MemStore() // Defer testing & making local/session stores until requested.
  // That way if we have errors here they can show up in devtools.

};
exports.stores = stores;
var backEnds = {
  local: 'localStorage',
  session: 'sessionStorage'
};

function tryGetWebStore(backEnd, dispatch) {
  var store = new WebStore(backEnd);
  var fallbackStore = stores.memory;
  var storeTest = longString();
  var testKey = storePrefix + 'x.x';

  try {
    store._setItem(testKey, storeTest);

    if (store.getItem(testKey) !== storeTest) {
      dispatch(err("".concat(backEnd, " init failed set/get, falling back to memory")));
      return fallbackStore;
    }

    store.removeItem(testKey);
    return store;
  } catch (e) {
    dispatch(err("".concat(backEnd, " init first try failed; clearing and retrying")));
  }

  try {
    store.clear();

    store._setItem(testKey, storeTest);

    if (store.getItem(testKey) !== storeTest) {
      throw new Error('nope');
    }

    store.removeItem(testKey);
    dispatch(err("".concat(backEnd, " init set/get succeeded after clearing!")));
    return store;
  } catch (e) {
    dispatch(err("".concat(backEnd, " init still failed, falling back to memory")));
    return fallbackStore;
  }
}

function getStore(type, dispatch) {
  if (!stores[type]) {
    stores[type] = tryGetWebStore(backEnds[type], dispatch);
  }

  return stores[type];
}

var noopTransform = {
  extract: function extract(propValue) {
    return propValue;
  },
  apply: function apply(storedValue, _propValue) {
    return storedValue;
  }
};

var getTransform = function getTransform(element, propName, propPart) {
  if (element.persistenceTransforms && element.persistenceTransforms[propName]) {
    if (propPart) {
      return element.persistenceTransforms[propName][propPart];
    }

    return element.persistenceTransforms[propName];
  }

  return noopTransform;
};

var getValsKey = function getValsKey(id, persistedProp, persistence) {
  return "".concat((0, _dependencies.stringifyId)(id), ".").concat(persistedProp, ".").concat(JSON.stringify(persistence));
};

var getProps = function getProps(layout) {
  var props = layout.props,
      type = layout.type,
      namespace = layout.namespace;

  if (!type || !namespace) {
    // not a real component - just need the props for recursion
    return {
      props: props
    };
  }

  var id = props.id,
      persistence = props.persistence;

  var element = _registry["default"].resolve(layout);

  var getVal = function getVal(prop) {
    return props[prop] || (element.defaultProps || {})[prop];
  };

  var persisted_props = getVal('persisted_props');
  var persistence_type = getVal('persistence_type');
  var canPersist = id && persisted_props && persistence_type;
  return {
    canPersist: canPersist,
    id: id,
    props: props,
    element: element,
    persistence: persistence,
    persisted_props: persisted_props,
    persistence_type: persistence_type
  };
};

function recordUiEdit(layout, newProps, dispatch) {
  var _getProps = getProps(layout),
      canPersist = _getProps.canPersist,
      id = _getProps.id,
      props = _getProps.props,
      element = _getProps.element,
      persistence = _getProps.persistence,
      persisted_props = _getProps.persisted_props,
      persistence_type = _getProps.persistence_type;

  if (!canPersist || !persistence) {
    return;
  }

  (0, _ramda.forEach)(function (persistedProp) {
    var _persistedProp$split = persistedProp.split('.'),
        _persistedProp$split2 = _slicedToArray(_persistedProp$split, 2),
        propName = _persistedProp$split2[0],
        propPart = _persistedProp$split2[1];

    if (newProps[propName] !== undefined) {
      var storage = getStore(persistence_type, dispatch);

      var _getTransform = getTransform(element, propName, propPart),
          extract = _getTransform.extract;

      var valsKey = getValsKey(id, persistedProp, persistence);
      var originalVal = extract(props[propName]);
      var newVal = extract(newProps[propName]); // mainly for nested props with multiple persisted parts, it's
      // possible to have the same value as before - should not store
      // in this case.

      if (originalVal !== newVal) {
        if (storage.hasItem(valsKey)) {
          originalVal = storage.getItem(valsKey)[1];
        }

        var vals = originalVal === undefined ? [newVal] : [newVal, originalVal];
        storage.setItem(valsKey, vals, dispatch);
      }
    }
  }, persisted_props);
}
/*
 * Used for entire layouts (on load) or partial layouts (from children
 * callbacks) to apply previously-stored UI edits to components
 */


function applyPersistence(layout, dispatch) {
  if ((0, _ramda.type)(layout) !== 'Object' || !layout.props) {
    return layout;
  }

  return persistenceMods(layout, layout, [], dispatch);
}

var UNDO = true;

function modProp(key, storage, element, props, persistedProp, update, undo) {
  if (storage.hasItem(key)) {
    var _storage$getItem = storage.getItem(key),
        _storage$getItem2 = _slicedToArray(_storage$getItem, 2),
        newVal = _storage$getItem2[0],
        originalVal = _storage$getItem2[1];

    var fromVal = undo ? newVal : originalVal;
    var toVal = undo ? originalVal : newVal;

    var _persistedProp$split3 = persistedProp.split('.'),
        _persistedProp$split4 = _slicedToArray(_persistedProp$split3, 2),
        propName = _persistedProp$split4[0],
        propPart = _persistedProp$split4[1];

    var transform = getTransform(element, propName, propPart);

    if ((0, _ramda.equals)(fromVal, transform.extract(props[propName]))) {
      update[propName] = transform.apply(toVal, propName in update ? update[propName] : props[propName]);
    } else {
      // clear this saved edit - we've started with the wrong
      // value for this persistence ID
      storage.removeItem(key);
    }
  }
}

function persistenceMods(layout, component, path, dispatch) {
  var _getProps2 = getProps(component),
      canPersist = _getProps2.canPersist,
      id = _getProps2.id,
      props = _getProps2.props,
      element = _getProps2.element,
      persistence = _getProps2.persistence,
      persisted_props = _getProps2.persisted_props,
      persistence_type = _getProps2.persistence_type;

  var layoutOut = layout;

  if (canPersist && persistence) {
    var storage = getStore(persistence_type, dispatch);
    var update = {};
    (0, _ramda.forEach)(function (persistedProp) {
      return modProp(getValsKey(id, persistedProp, persistence), storage, element, props, persistedProp, update);
    }, persisted_props);

    for (var propName in update) {
      layoutOut = (0, _ramda.set)((0, _ramda.lensPath)(path.concat('props', propName)), update[propName], layoutOut);
    }
  } // recurse inward


  var children = props.children;

  if (Array.isArray(children)) {
    children.forEach(function (child, i) {
      if ((0, _ramda.type)(child) === 'Object' && child.props) {
        layoutOut = persistenceMods(layoutOut, child, path.concat('props', 'children', i), dispatch);
      }
    });
  } else if ((0, _ramda.type)(children) === 'Object' && children.props) {
    layoutOut = persistenceMods(layoutOut, children, path.concat('props', 'children'), dispatch);
  }

  return layoutOut;
}
/*
 * When we receive new explicit props from a callback,
 * these override UI-driven edits of those exact props
 * but not for props nested inside children
 */


function prunePersistence(layout, newProps, dispatch) {
  var _getProps3 = getProps(layout),
      canPersist = _getProps3.canPersist,
      id = _getProps3.id,
      props = _getProps3.props,
      persistence = _getProps3.persistence,
      persisted_props = _getProps3.persisted_props,
      persistence_type = _getProps3.persistence_type,
      element = _getProps3.element;

  var getFinal = function getFinal(propName, prevVal) {
    return propName in newProps ? newProps[propName] : prevVal;
  };

  var finalPersistence = getFinal('persistence', persistence);

  if (!canPersist || !(persistence || finalPersistence)) {
    return newProps;
  }

  var finalPersistenceType = getFinal('persistence_type', persistence_type);
  var finalPersistedProps = getFinal('persisted_props', persisted_props);
  var persistenceChanged = finalPersistence !== persistence || finalPersistenceType !== persistence_type || finalPersistedProps !== persisted_props;

  var notInNewProps = function notInNewProps(persistedProp) {
    return !(persistedProp.split('.')[0] in newProps);
  };

  var update = {};
  var depersistedProps = props;

  if (persistenceChanged && persistence) {
    // clear previously-applied persistence
    var storage = getStore(persistence_type, dispatch);
    (0, _ramda.forEach)(function (persistedProp) {
      return modProp(getValsKey(id, persistedProp, persistence), storage, element, props, persistedProp, update, UNDO);
    }, (0, _ramda.filter)(notInNewProps, persisted_props));
    depersistedProps = (0, _ramda.mergeRight)(props, update);
  }

  if (finalPersistence) {
    var finalStorage = getStore(finalPersistenceType, dispatch);

    if (persistenceChanged) {
      // apply new persistence
      (0, _ramda.forEach)(function (persistedProp) {
        return modProp(getValsKey(id, persistedProp, finalPersistence), finalStorage, element, depersistedProps, persistedProp, update);
      }, (0, _ramda.filter)(notInNewProps, finalPersistedProps));
    } // now the main point - clear any edit of a prop that changed
    // note that this is independent of the new prop value.


    var transforms = element.persistenceTransforms || {};

    for (var propName in newProps) {
      var propTransforms = transforms[propName];

      if (propTransforms) {
        for (var propPart in propTransforms) {
          finalStorage.removeItem(getValsKey(id, "".concat(propName, ".").concat(propPart), finalPersistence));
        }
      } else {
        finalStorage.removeItem(getValsKey(id, propName, finalPersistence));
      }
    }
  }

  return persistenceChanged ? (0, _ramda.mergeRight)(newProps, update) : newProps;
}