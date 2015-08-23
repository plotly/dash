'use strict';

import AppDispatcher from '../dispatchers/AppDispatcher';
import BaseStore from './BaseStore';
import AppConstants from '../constants/AppConstants';
import Collection from 'ampersand-collection';
import AppActions from '../actions/AppActions';

var _appStore = {
    firstDropdown: {
        'options': [
            {'val': 'seafood', 'name': 'Fish'},
            {'val': 'meat', 'name': 'Meats'},
            {'val': 'vegetables', 'name': 'Les Legumes'}
        ],
        'selected': 'seafood',
        'id': 'firstDropdown',
        'element': 'dropdown'
    },

    secondDropdown: {
        'options': [
            {'val': 'iris', 'name': 'iriss'},
            {'val': 'cosmos', 'name': 'c0sMOs'},
            {'val': 'sunflr', 'name': 'sunflowerz'}
        ],
        'selected': 'cosmos',
        'id': 'secondDropdown',
        'element': 'dropdown'
    },

    firstRadio: {
        'options': [
            {'val': 'seafood', 'name': 'Fish'},
            {'val': 'meat', 'name': 'Meats'},
            {'val': 'vegetables', 'name': 'Les Legumes'}
        ],
        'selected': 'seafood',
        'element': 'radio'
    },

    secondRadio: {
        'options': [
            {'val': 'iris', 'name': 'iriss'},
            {'val': 'cosmos', 'name': 'c0sMOs'},
            {'val': 'sunflr', 'name': 'sunflowerz'}
        ],
        'selected': 'cosmos',
        'element': 'radio'
    }
};

var AppStore = BaseStore.extend({
    getState: function (){
        return _appStore;
    }
});


var actions = function(action) {
    switch(action.event) {

    case AppConstants.UPDATEDROPDOWNVALUE:
        _appStore[action.dropdownId].selected = action.dropdownValue;
        AppStore.emitChange();
    }
};

AppDispatcher.register(actions);

module.exports = AppStore;
