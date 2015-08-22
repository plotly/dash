'use strict';

import AppConstants from '../constants/AppConstants';
import AppDispatcher from '../dispatchers/AppDispatcher';
import AppState from 'ampersand-app';
import request from 'request';

var AppActions = {
    setFirstDropdownValue: function(dropdownValue) {
        AppDispatcher.dispatch({
            event: AppConstants.SETFIRSTDROPDOWNVALUE,
            dropdownValue: dropdownValue
        })
    },
    setFirstRadioButtonValue: function(radioButtonValue) {
        AppDispatcher.dispatch({
            event: AppConstants.SETFIRSTRADIOBUTTONVALUE,
            radioButtonValue: radioButtonValue
        })
    }
};

module.exports = AppActions;
window.AppActions = AppActions;
