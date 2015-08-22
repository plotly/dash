'use strict';

import AppDispatcher from '../dispatchers/AppDispatcher';
import BaseStore from './BaseStore';
import AppConstants from '../constants/AppConstants';
import Collection from 'ampersand-collection';
import AppActions from '../actions/AppActions';

var _appStore = {
    firstDropdown: [
        {'val': 'seafood', 'name': 'Fish'},
        {'val': 'meat', 'name': 'Meats'},
        {'val': 'vegetables', 'name': 'Les Legumes'}
    ],
    firstDropdownSelection: 'seafood',
    firstRadio: [
        {'val': 'monday', 'name': 'Monday'},
        {'val': 'tuesday', 'name': 'Tuesday'},
        {'val': 'wednesday', 'name': 'Wednesday'}
    ],
    firstRadioSelection: 'tuesday'
};

var AppStore = BaseStore.extend({
    getFirstDropdown: function(){
        return _appStore.firstDropdown.slice();
    },
    getFirstDropdownSelection: function() {
        return _appStore.firstDropdownSelection;
    },

    getFirstRadio: function() {
        return _appStore.firstRadio.slice();
    },
    getFirstRadioSelection: function(){
        return _appStore.firstRadioSelection;
    }
});


var actions = function(action) {
    switch(action.event) {

    case AppConstants.SETFIRSTDROPDOWNVALUE:
        _appStore.firstDropdownSelection = action.dropdownValue;
        AppStore.emitChange();

    case AppConstants.SETFIRSTRADIOBUTTONVALUE:
        _appStore.firstRadioSelection = action.radioButtonValue;
        AppStore.emitChange();

    }
};

AppDispatcher.register(actions);

module.exports = AppStore;
