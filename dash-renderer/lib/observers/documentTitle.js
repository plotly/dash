"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;

var updateTitle = function updateTitle(getState) {
  var _getState = getState(),
      config = _getState.config,
      isLoading = _getState.isLoading;

  var update_title = config === null || config === void 0 ? void 0 : config.update_title;

  if (!update_title) {
    return;
  }

  if (isLoading) {
    if (document.title !== update_title) {
      _observer.title = document.title;
      document.title = update_title;
    }
  } else {
    if (document.title === update_title) {
      document.title = _observer.title;
    } else {
      _observer.title = document.title;
    }
  }
};

var _observer = {
  inputs: ['isLoading'],
  mutationObserver: undefined,
  observer: function observer(_ref) {
    var getState = _ref.getState;

    var _getState2 = getState(),
        config = _getState2.config;

    if (_observer.config !== config) {
      var _observer$mutationObs;

      _observer.config = config;
      (_observer$mutationObs = _observer.mutationObserver) === null || _observer$mutationObs === void 0 ? void 0 : _observer$mutationObs.disconnect();
      _observer.mutationObserver = new MutationObserver(function () {
        return updateTitle(getState);
      });
      var title = document.querySelector('title');

      if (title) {
        _observer.mutationObserver.observe(title, {
          subtree: true,
          childList: true,
          attributes: true,
          characterData: true
        });
      }
    }

    updateTitle(getState);
  }
};
var _default = _observer;
exports["default"] = _default;