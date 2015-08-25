'use strict';

import AppConstants from '../constants/AppConstants';
import AppDispatcher from '../dispatchers/AppDispatcher';
import AppState from 'ampersand-app';
import request from 'request';
import AppStore from '../stores/AppStore';


var AppActions = {
    setSelectedValue: function(id, value) {
        AppDispatcher.dispatch({
            event: AppConstants.SETSELECTEDVALUE,
            id: id,
            value: value
        })

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

    updateGraph: function(targetId, previous, store) {
        let body = JSON.stringify({
            'appStore': store,
            'targetId': targetId,
            'previousValue': previous
        });
        request({
            method: 'POST',
            body: body,
            url: 'http://localhost:8080/api'
        }, function(err, res, body) {
            if(!err && res.statusCode == 200) {
                // In the future, this can just be stuff that changed
                body = JSON.parse(body);
                AppDispatcher.dispatch({
                    event: AppConstants.UPDATEGRAPH,
                    graphid: body['appStore']['graph']['id'],
                    figure: body['appStore']['graph']['figure']
                });
            }
        });
    },

    askServerForUpdates: function(targetId, previous, store) {
        console.log('Making request');
        request({
            method: 'POST',
            body: JSON.stringify({
                'appStore': store,
                'targetId': targetId,
                'previousValue': previous
            }),
            url: 'http://localhost:8080/api'
        }, function(err, res, body) {
            if(!err && res.statusCode == 200) {
                body = JSON.parse(body);
                // In the future, this can just be stuff that changed
                AppDispatcher.dispatch({
                    event: AppConstants.SERVERUPDATE,
                    appStore: body['appStore']
                });
            }
        });
    }
};

module.exports = AppActions;
window.AppActions = AppActions;
