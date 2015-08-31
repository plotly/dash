'use strict';

import AppDispatcher from '../dispatchers/AppDispatcher';
import BaseStore from './BaseStore';
import AppConstants from '../constants/AppConstants';
import Collection from 'ampersand-collection';
import AppActions from '../actions/AppActions';
import request from 'request';

var _appStore = {}
var _outdated = []

var AppStore = BaseStore.extend({
    getState: function (){
        return {
            'components': _appStore,
            'meta': {
                'outdated': _outdated
            }
        };
    }
});

function flagChildrenAsOutdated(id) {
        // flag children children as outdated
    for(var i=0; i<_appStore[id].children.length; i++) {
        _outdated.push(_appStore[id].children[i]);
    }
}

var actions = function(action) {
    var previous;
    let evt = action.event;
    console.log('DISPATCH-STORE:', evt, action.id);
    switch(evt) {
        case AppConstants.SETSELECTEDVALUE:
            previous = _appStore[action.id].selected;
            _appStore[action.id].selected = action.value;
            flagChildrenAsOutdated(action.id);
            AppStore.emitChange();
            break;

        case AppConstants.SETVALUE:
            previous = _appStore[action.id].value;
            _appStore[action.id].value = action.value;
            AppStore.emitChange();
            break;

        case AppConstants.SETCHECKED:
            var options = _appStore[action.id].options;
            for(var i=0; i<options.length; i++){
                if(options[i].id == action.id) {
                    previous = options[i].isChecked;
                    options[i].isChecked = action.isChecked;
                }
            }
            AppStore.emitChange();
            break;

        case AppConstants.UPDATEGRAPH:
            _appStore[action.graphid].figure = action.figure;
            _appStore[action.graphid].height = action.figure.layout.height + 'px';
            AppStore.emitChange();
            break;

        case 'SETSTORE':
            _appStore = action.appStore;
            AppStore.emitChange();
            break;

        case AppConstants.UPDATECOMPONENT:
            _appStore[action.id] = action.component;
            flagChildrenAsOutdated(action.id);
            AppStore.emitChange();
            break;

        case AppConstants.UNMARK_COMPONENT_AS_OUTDATED:
            // remove all elements in outdated with id action.id
            for(var i = _outdated.length - 1; i >= 0; i--) {
                if(_outdated[i] === action.id) {
                    _outdated.splice(i, 1);
                }
            }
            // emit change?
            // AppStore.emitChange();
            break;
    }
    console.log('CLEAR-STORE:', evt, action.id);
};

AppDispatcher.register(actions);

exports.AppStore = AppStore;

(function(){
    AppActions.initialize();
})();

