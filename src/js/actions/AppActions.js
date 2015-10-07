'use strict';

import AppConstants from '../constants/AppConstants';
import AppDispatcher from '../dispatchers/AppDispatcher';
import AppState from 'ampersand-app';
import request from 'request';
import {AppStore} from '../stores/AppStore';

var _pendingRequests = {};

var AppActions = {

    setSelectedValue: function(id, value) {
        AppDispatcher.dispatch({
            event: AppConstants.SETSELECTEDVALUE,
            id: id,
            value: value
        })
        this.updateDependents(id);
    },

    updateDependents: function(id) {
        // now update the outdated components
        let outdated;

        let dependents = AppStore.getState().meta.dependents;
        if(id in dependents) {
            dependents = dependents[id];

            for(var i=0; i<dependents.length; i++) {
                outdated = AppStore.getState().meta.outdated;
                if(dependents[i] in outdated && outdated[dependents[i]].length === 0) {
                    this.getComponentState(dependents[i]);
                }
            }
        }

    },

    getInitialState: function() {
        AppDispatcher.dispatch({
            event: AppConstants.GETINITIALSTATE
        })
    },

    setValue: function(id, value) {
        AppDispatcher.dispatch({
            event: AppConstants.SETKEY,
            id: id,
            key: 'value',
            value: value
        });
        this.updateDependents(id);
    },

    setKey: function(id, key, value) {
        AppDispatcher.dispatch({
            event: AppConstants.SETKEY,
            id: id,
            key: key,
            value: value
        });
        this.updateDependents(id);
    },

    setCheckedValue: function(checklistId, checkboxId, isChecked) {
        let component = AppStore.getComponent(checklistId);
        let options = component.props.options;

        for(var i=0; i<options.length; i++) {
            if(options[i].id === checkboxId) {
                options[i].checked = isChecked;
            }
        }

        AppDispatcher.dispatch({
            event: AppConstants.SETKEY,
            id: checklistId,
            key: 'options',
            value: options
        });

        this.updateDependents(checklistId);

    },

    getComponentState: function(id) {
        // Request is pending, so remove it from this list so that
        // re-rendering doesn't continuously restart requests.
        var that = this;
        AppDispatcher.dispatch({
            event: AppConstants.UNMARK_COMPONENT_AS_OUTDATED,
            id: id
        });

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
                component = body.response;
                AppDispatcher.dispatch({
                    event: AppConstants.UPDATECOMPONENT,
                    component: component,
                    id: component.id
                });
                // TODO: unify this call somehow.
                that.updateDependents(id);
            } else {
                // ...
            }
        });

    },

    initialize: function() {
        var that = this;
        request({
            method: 'GET',
            url: 'http://localhost:8080/initialize'
        }, function(err, res, body) {
            if(!err && res.statusCode == 200) {
                body = JSON.parse(body);
                AppDispatcher.dispatch({
                    event: 'SETSTORE',
                    appStore: body
                });

                let outdated = AppStore.getState().meta.outdated;
                let dependents = AppStore.getState().meta.dependents;
                // update all the elements that depend on the parent elements
                // that have no dependencies.
                for(var i in dependents) {
                    if(!(i in outdated)) {
                        that.updateDependents(i);
                    }
                }
            }
        });
    }
};

module.exports = AppActions;
