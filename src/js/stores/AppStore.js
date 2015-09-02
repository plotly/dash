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
    },
    getComponent: function (component_id) {
        // very confusing tree traversal recursion.
        var out;
        function traverse(o) {
            if(o.constructor === Array) {
                for(var i=0; i<o.length; i++) {
                    if(traverse(o[i])){return;}
                }
            } else if(o.props.id && o.props.id === component_id) {
                out = o;
                return true;
            } else if(o.children && o.children.constructor === Array) {
                if(traverse(o.children)){return;}
            }
        }
        traverse(_appStore);
        return out;
    },
    getComponentDependencies: function(component_id) {
        let dependencies_ids = this.getComponent(component_id).props.dependencies;
        let dependencies = {};
        let component;
        for(var i=0; i<dependencies_ids.length; i++) {
            component = this.getComponent(dependencies_ids[i]);
            delete component.children;
            dependencies[dependencies_ids[i]] = component;
        }
        return dependencies;
    }
});

function flagChildrenAsOutdated(component_id) {
    // find which components depend on this component, and flag them as outdated
    if(!component_id){ return; } // not all components have ids
    var dependentIds = []
    function traverse(o) {
        if(o.constructor === Array) {
            for(var i=0; i<o.length; i++) {
                traverse(o[i]);
            }
        } else {
            if(o.props.dependencies && o.props.dependencies.indexOf(component_id) > -1) {
                dependentIds.push(o.props.id);
            }
            if(o.children && o.children.constructor === Array) {
                traverse(o.children)
            }
        }
    }
    traverse(_appStore);
    console.log('dependentIds', dependentIds);
    for(var i=0; i<dependentIds.length; i++) {
        _outdated.push(dependentIds[i]);
    }
}

var actions = function(action) {
    var previous;
    let evt = action.event;
    console.log('DISPATCH-STORE:', evt, action.id);
    if(action.id){
        var component = AppStore.getComponent(action.id);
    }
    switch(evt) {
        case AppConstants.SETSELECTEDVALUE:
            component.props.selected = action.value;
            flagChildrenAsOutdated(component.props.id);
            AppStore.emitChange();
            break;

        /*
        case AppConstants.SETVALUE:
            _appStore[action.id].value = action.value;
            flagChildrenAsOutdated(component_id);
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
            // flagChildrenAsOutdated(action.id);
            AppStore.emitChange();
            break;
        */
        case AppConstants.UPDATEGRAPH:
            component.props.figure = action.figure;
            component.props.height = action.figure.layout.height + 'px';
            flagChildrenAsOutdated(component.props.id);
            AppStore.emitChange();
            break;

        case 'SETSTORE':
            _appStore = action.appStore;
            AppStore.emitChange();
            break;

        case AppConstants.UPDATECOMPONENT:
            // from the server
            console.log(component, '\n^^^\n', action.component);
            // javascript i'm so bad at you. mutate reference of object.
            // should probably also delete untransferred keys.
            for(var k in action.component) {
                component[k] = action.component[k];
            }
            flagChildrenAsOutdated(component.props.id);
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

