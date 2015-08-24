'use strict';

import AppDispatcher from '../dispatchers/AppDispatcher';
import BaseStore from './BaseStore';
import AppConstants from '../constants/AppConstants';
import Collection from 'ampersand-collection';
import AppActions from '../actions/AppActions';
import request from 'request';

var _appStore = {}

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

    case AppConstants.GETINITIALSTATE:

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

(function(){
    AppActions.getInitialState();
})();

module.exports = AppStore;

