'use strict';

import AppConstants from '../constants/AppConstants';
import AppDispatcher from '../dispatchers/AppDispatcher';
import AppState from 'ampersand-app';
import request from 'request';
import {AppStore} from '../stores/AppStore';

var _pendingRequests = {};

var AppActions = {
    setSelectedValue: function(id, value) {
        console.log('DISPATCH: SETSELECTEDVALUE');
        AppDispatcher.dispatch({
            event: AppConstants.SETSELECTEDVALUE,
            id: id,
            value: value
        })
        console.log('CLEAR: SETSELECTEDVALUE');
    },

    getInitialState: function() {
        AppDispatcher.dispatch({
            event: AppConstants.GETINITIALSTATE
        })
    },

    setValue: function(id, value) {
        AppDispatcher.dispatch({
            event: AppConstants.SETVALUE,
            id: id,
            value: value
        })
    },

    setCheckedValue: function(id, isChecked) {
        AppDispatcher.dispatch({
            event: AppConstants.SETCHECKED,
            id: id,
            isChecked: isChecked
        })
    },

    getLongestPathBetweenComponents: function(steps, parent_id, target_id) {
        var children = AppStore.getComponentDependencies(parent_id)
        if(children.indexOf(target_id) > -1){
            return steps+1;
        } else {
            for(var i=0; i<children.length; i++) {
                steps = Math.max(steps, this.getLongestPathBetweenComponents(steps, children[i], target_id))
            }
            return steps;
        }
    },

    getComponentState: function(id) {
        // Request is pending, so remove it from this list so that
        // re-rendering doesn't continuously restart requests.
        console.log('DISPATCH: UNMARK_COMPONENT_AS_OUTDATED', id);
        AppDispatcher.dispatch({
            event: AppConstants.UNMARK_COMPONENT_AS_OUTDATED,
            id: id
        });
        console.log('CLEAR: UNMARK_COMPONENT_AS_OUTDATED', id);
        // Abort pending requests
        if(id in _pendingRequests){
            _pendingRequests[id].abort();
            _pendingRequests[id] = null;
        }

        // Get the component's dependencies
        let parents = AppStore.getComponentDependencies(id);
        let body = {'target': AppStore.getComponent(id), 'parents': parents};
        let component;
        // Add additional request
        _pendingRequests[id] = request({
            method: 'POST',
            body: JSON.stringify(body),
            url: 'http://localhost:8080/interceptor'
        }, function(err, res, body) {
            if(!err && res.statusCode == 200) {
                body = JSON.parse(body);
                console.log('DISPATCH: UPDATECOMPONENT', body.response.id);
                component = body.response;
                AppDispatcher.dispatch({
                    event: AppConstants.UPDATECOMPONENT,
                    component: component,
                    id: component.props.id
                });
                console.log('CLEAR: UPDATECOMPONENT', body.response.id);
            } else {
                // ...
            }
        });
    },

    initialize: function() {
        request({
            method: 'GET',
            url: 'http://localhost:8080/initialize'
        }, function(err, res, body) {
            if(!err && res.statusCode == 200) {
                console.log('initialize: ', body);
                body = JSON.parse(body);
                console.log('DISPATCH: SETSTORE');
                AppDispatcher.dispatch({
                    event: 'SETSTORE',
                    appStore: body
                });
                console.log('CLEAR: SETSTORE');
            }
        });
    }
};

module.exports = AppActions;
