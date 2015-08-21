'use strict';

import AppConstants from '../constants/AppConstants';
import AppDispatcher from '../dispatchers/AppDispatcher';
import AppState from 'ampersand-app';
import request from 'request';

var AppActions = {
    setFirstD: function(currentD) {
        AppDispatcher.dispatch({
            event: AppConstants.SETCURRENTD,
            currentD: currentD
        });
    },
    getSecondDropDown: function(currentD) {
        request.get('http://localhost:8080/api', function(err, res, body){
            debugger;
            if(!err && res.statusCode == 200) {
                AppDispatcher.dispatch({
                    event: AppConstants.SETSECONDD,
                    secondDropdown: JSON.parse(body)[currentD]
                });
            }
        })
    }
};

module.exports = AppActions;
window.AppActions = AppActions;
