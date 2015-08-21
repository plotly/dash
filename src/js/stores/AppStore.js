'use strict';

import AppDispatcher from '../dispatchers/AppDispatcher';
import BaseStore from './BaseStore';
import AppConstants from '../constants/AppConstants';
import Collection from 'ampersand-collection';
import AppActions from '../actions/AppActions'

var _appStore = {
    currentD: 'seafood',
    firstDropDown: [
        {'val': 'seafood', 'name': 'Fish'},
        {'val': 'meat', 'name': 'Meats'},
        {'val': 'vegetables', 'name': 'Les Legumes'}
    ],
    secondDropDown: []
}

var AppStore = BaseStore.extend({
    getFirstDropDown: function(){
        return _appStore.firstDropDown.slice()
    },
    getSecondDropDown: function(){
        return _appStore.secondDropDown.slice()
    }
});

var actions = function(action) {
    switch(action.event) {

    case AppConstants.SETSECONDD:
        _appStore.secondDropDown = action.secondDropDown;
        AppStore.emitChange(); // always put here after very action
    }
};

AppDispatcher.register(actions);

(function(){
    AppActions.getSecondDropDown('seafood');
})();

module.exports = AppStore;
