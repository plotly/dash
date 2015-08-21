'use strict';

import AppDispatcher from '../dispatchers/AppDispatcher';
import BaseStore from './BaseStore';
import AppConstants from '../constants/AppConstants';
import Collection from 'ampersand-collection';

var _appStore = {
    currentD: 'seafood',
    firstDropDown: [
        {'val': 'seafood', 'name': 'Fish'},
        {'val': 'meat', 'name': 'Meats'},
        {'val': 'vegetables', 'name': 'Les Legumes'}
    ],

    secondDropDown: {
        'seafood': [
            {'val': 'smoked-salmon', 'name': 'Fresh Smoked Salmon'},
            {'val': 'smoked-trout', 'name': 'Wild Alaska Trout'},
            {'val': 'flying-fish', 'name': 'A Barbados Special'}
        ],
        'meat': [
            {'val': 'hamburger', 'name': 'Palace Burger'},
            {'val': 'sausage', 'name': 'Chez Vito Turkey Sausage'}
        ],
        'vegetables': [
            {'val': 'rutabegga', 'name': 'Rudabagga'},
            {'val': 'carrots', 'name': 'Rainbow Carrots'},
            {'val': 'fennel', 'name': 'Sliced Fennal'}
        ]
    }
}

var AppStore = BaseStore.extend({
    getFirstDropDown: function(){
        return _appStore.firstDropDown.slice()
    },
    getSecondDropDown: function(){
        return _appStore.secondDropDown[_appStore.currentD].slice()
    },
    getCurrentD: function(){
        return _appStore.currentD
    }
});

var actions = function(action) {
    switch(action.event) {

    case AppConstants.SETCURRENTD:
        AppStore.emitChange();

    case AppConstants.SETSECONDD:
        _appStore.

    }
};

AppDispatcher.register(actions);
module.exports = AppStore;
