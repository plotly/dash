'use strict';

import AppDispatcher from '../dispatchers/AppDispatcher';
import BaseStore from './BaseStore';
import AppConstants from '../constants/AppConstants';
import Collection from 'ampersand-collection';
import AppActions from '../actions/AppActions';
import request from 'request';

var _appStore = {
    firstDropdown: {
        'options': [
            {'val': 'seafood', 'label': 'Fish'},
            {'val': 'meat', 'label': 'Meats'},
            {'val': 'vegetables', 'label': 'Les Legumes'}
        ],
        'selected': 'seafood',
        'id': 'firstDropdown',
        'element': 'dropdown'
    },

    secondDropdown: {
        'options': [
            {'val': 'iris', 'label': 'iriss'},
            {'val': 'cosmos', 'label': 'c0sMOs'},
            {'val': 'sunflr', 'label': 'sunflowerz'}
        ],
        'selected': 'cosmos',
        'id': 'secondDropdown',
        'element': 'dropdown'
    },

    firstRadio: {
        'options': [
            {'val': 'seafood', 'label': 'Fish'},
            {'val': 'meat', 'label': 'Meats'},
            {'val': 'vegetables', 'label': 'Les Legumes'}
        ],
        'id': 'firstRadio',
        'name': 'foodGroup',
        'selected': 'seafood',
        'element': 'radio'
    },

    secondRadio: {
        'options': [
            {'val': 'iris', 'label': 'iriss'},
            {'val': 'cosmos', 'label': 'c0sMOs'},
            {'val': 'sunflr', 'label': 'sunflowerz'}
        ],
        'id': 'secondRadio',
        'name': 'flowers',
        'selected': 'cosmos',
        'element': 'radio'
    },

    firstCheckbox: {
        'options': [
            {'id': 'daisy', 'label': 'Dasiy', 'isChecked': true},
            {'id': 'dandalion', 'label': 'Dandalion', 'isChecked': false}
        ],
        'name': 'flowers-that-start-with-d'
    },

    firstSlider: {
        'min': 5,
        'max': 50,
        'step': 0.25,
        'value': 40,
        'id': 'firstSlider'
    },

    dateSlider: {
        'min': '2015-01-01 00:00:00',
        'max': '2015-05-03 00:00:00',
        'step': 1000*60*60*3, // 3 hours
        'value': '2015-04-01T08:00:00Z',
        'id': 'dateSlider'
    }
};

var AppStore = BaseStore.extend({
    getState: function (){
        return _appStore;
    }
});


var actions = function(action) {
    var previous;
    var targetId = action.id;
    switch(action.event) {
    case AppConstants.SETSELECTEDVALUE:
        previous = _appStore[action.id].selected;
        _appStore[action.id].selected = action.value;
        AppStore.emitChange();

    case AppConstants.SETVALUE:
        previous = _appStore[action.id].value;
        _appStore[action.id].value = action.value;
        AppStore.emitChange();

    case AppConstants.SETCHECKED:
        var options = _appStore['firstCheckbox'].options;
        for(var i=0; i<options.length; i++){
            if(options[i].id == action.id) {
                previous = options[i].isChecked;
                options[i].isChecked = action.isChecked;
            }
        }
        AppStore.emitChange();
    }

    request({
            method: 'POST',
            body: {
                'appStore': _appStore,
                'targetId': targetId,
                'previousValue': previous
            },
            json: true,
            url: 'http://localhost:8080/api'
        }, function(err, res, body) {
            if(!err && res.statusCode == 200) {
                _appStore = body['appStore'];
                AppStore.emitChange();
            }
        }
    );
};

AppDispatcher.register(actions);

module.exports = AppStore;
