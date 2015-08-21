'use strict';

import AppConstants from '../constants/AppConstants';
import AppDispatcher from '../dispatchers/AppDispatcher';
import AppState from 'ampersand-app';
import request from 'request';

var AppActions = {
    getSecondDropDown: function(currentD) {
        //debugger;
        request.get('http://localhost:8080/api', function(err, res, body){
            if(!err && res.statusCode == 200) {
                AppDispatcher.dispatch({
                    event: AppConstants.SETSECONDD,
                    secondDropDown: JSON.parse(body)[currentD]
                });
            }
        })
    }
};

module.exports = AppActions;
window.AppActions = AppActions;
