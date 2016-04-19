'use strict';

import AppDispatcher from '../dispatchers/AppDispatcher';
import BaseStore from './BaseStore';
import AppConstants from '../constants/AppConstants';
import AppActions from '../actions/AppActions';
import request from 'request';

var _appStore = {};
var _outdated = {};

var _dependents = {};   // {b: ['a', 'd']} -> b is the parent of 'a', 'd'
                        // 'a' and 'd' depend on 'b'
var _dependencies = {}; // {a: ['b', 'c']} -> a is the child of 'b' and 'c'
                        // 'a' depends on 'b' and 'c'

var AppStore = BaseStore.extend({
    getState: function (){
        return {
            'components': _appStore,
            'meta': {
                'outdated': _outdated,
                'dependencies': _dependencies,
                'dependents': _dependents
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
            } else if (typeof o === 'string' || o instanceof String) {
                return;
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
        if(dependencies_ids) {
            for(var i=0; i<dependencies_ids.length; i++) {
                component = this.getComponent(dependencies_ids[i]);
                delete component.children;
                dependencies[dependencies_ids[i]] = component;
            }
        }
        return dependencies;
    }
});

function initialize_relationships() {
    function traverse(o) {
        if(!(typeof o === 'string' || o instanceof String) && 'props' in o && 'id' in o.props && o.props.id) {
            if(o.props.dependencies) {
                for(var i=0; i<o.props.dependencies.length; i++) {
                    if(o.props.id in _dependencies) {
                        _dependencies[o.props.id].push(o.props.dependencies[i]);
                    } else {
                        _dependencies[o.props.id] = [o.props.dependencies[i]];
                    }
                }
            }
        } if(o.children && o.children.constructor === Array) {
            for(var i=0; i<o.children.length; i++) {
                traverse(o.children[i]);
            }
        }
    }

    traverse(_appStore);

    for(var i in _dependencies) {
        for(var j=0; j<_dependencies[i].length; j++){
            if(_dependencies[i][j] in _dependents) {
                _dependents[_dependencies[i][j]].push(i);
            } else {
                _dependents[_dependencies[i][j]] = [i];
            }
        }
    }
}

function initialize_outdated_relationships() {
    // Set the app into an outdated state so that all the
    // callbacks are fired on page load.
    _outdated = {};
    for(var i in _dependencies) {
        _outdated[i] = _dependencies[i].slice();
    }
    // remove items that have no dependencies
    for(var i in _outdated) {
        for(var j=_outdated[i].length - 1; j >= 0; j--) {
            if(!(_outdated[i][j] in _outdated)) {
                _outdated[i].splice(j, 1);
            }
        }
    }
}

function flagChildrenAsOutdated(component_id) {
    /*
    _outdated = {
        'A': ['B', 'C'],    // "A" is outdated, needs "B" and "C" to update
        'B': ['D'],         // "B" is outdated, is waiting on "C" to update
        'C': []             // "C" is outdated, is ready to ask the server for updates
                            // and all of its dependencies are up-to-date.
    }

    If "A" depends on "B" depends on "C", then:
    flagChildrenAsOutdated("C"):
        _oudated -> {A: [B], B: []}
    */

    function traverse(component_id) {
        if(component_id in _dependents && _dependents[component_id].length > 0) {
            for(var i=0; i<_dependents[component_id].length; i++) {
                if(_dependents[component_id][i] in _outdated) {
                    _outdated[_dependents[component_id][i]].push(component_id);
                } else {
                    _outdated[_dependents[component_id][i]] = [component_id];
                }
                traverse(_dependents[component_id][i]);
            }
        }
    }

    traverse(component_id);

    /* Now remove component_id from _oudated */

    for(var i in _outdated) {
        for(var j = _outdated[i].length - 1; j >= 0; j--) {
            if(_outdated[i][j] === component_id) {
               _outdated[i].splice(j, 1);
            }
        }
    }


}

var actions = function(action) {
    var previous;
    let evt = action.event;
    if(action.id){
        var component = AppStore.getComponent(action.id);
    }
    switch(evt) {
        case AppConstants.SETSELECTEDVALUE:
            component.props.selected = action.value;
            flagChildrenAsOutdated(component.props.id);
            AppStore.emitChange();
            break;

        case AppConstants.UPDATEGRAPH:
            component.props.figure = action.figure;
            component.props.height = action.figure.layout.height + 'px';
            flagChildrenAsOutdated(component.props.id);
            AppStore.emitChange();
            break;

        case AppConstants.SETKEY:
            component.props[action.key] = action.value;
            flagChildrenAsOutdated(component.props.id);
            AppStore.emitChange();
            break;


        case 'SETSTORE':
            _appStore = action.appStore;
            initialize_relationships();
            initialize_outdated_relationships();
            AppStore.emitChange();
            break;

        case AppConstants.UPDATECOMPONENT:
            // from the server
            if('children' in action.component) {
                component.children = action.component.children;
            }
            for(var prop in action.component.props) {
                component.props[prop] = action.component.props[prop];
            }
            flagChildrenAsOutdated(component.props.id);
            AppStore.emitChange();
            break;

        case AppConstants.UNMARK_COMPONENT_AS_OUTDATED:
            if(action.id in _outdated && _outdated[action.id].length === 0) {
                delete _outdated[action.id];
            }
            // emit change?
            // AppStore.emitChange();
            break;
    }
};

AppDispatcher.register(actions);

exports.AppStore = AppStore;


(function(){
    AppActions.initialize();
})();

