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
    console.log('event: ', action.event);
    let evt = action.event;
    if(evt === AppConstants.SETSELECTEDVALUE){
        previous = _appStore[action.id].selected;
        _appStore[action.id].selected = action.value;
        AppStore.emitChange();
        AppActions.updateGraph(targetId, previous, _appStore);
    } else if (evt === AppConstants.SETVALUE) {
        previous = _appStore[action.id].value;
        _appStore[action.id].value = action.value;
        AppStore.emitChange();
        AppActions.updateGraph(targetId, previous, _appStore);
    } else if (evt === AppConstants.SETCHECKED) {
        var options = _appStore[action.id].options;
        for(var i=0; i<options.length; i++){
            if(options[i].id == action.id) {
                previous = options[i].isChecked;
                options[i].isChecked = action.isChecked;
            }
        }
        AppStore.emitChange();
        AppActions.updateGraph(targetId, previous, _appStore);
    } else if (evt === AppConstants.UPDATEGRAPH) {
        _appStore[action.graphid].figure = action.figure;
        _appStore[action.graphid].height = action.figure.layout.height + 'px';
        AppStore.emitChange();
    } else if (evt === AppConstants.SERVERUPDATE) {
        _appStore = action.appStore;
        AppStore.emitChange();
    }
};

AppDispatcher.register(actions);

(function(){
    AppActions.askServerForUpdates('', '', _appStore);
})();

module.exports = AppStore;

