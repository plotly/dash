'use strict';

import AppConstants from '../constants/AppConstants';
import AppDispatcher from '../dispatchers/AppDispatcher';
import AppState from 'ampersand-app';
import request from 'request';

var AppActions = {
    setDropdownAndRadioValue: function(id, value) {
        AppDispatcher.dispatch({
            event: AppConstants.UPDATEDROPDOWNANDRADIOVALUE,
            id: id,
            value: value
        })
    }
};

module.exports = AppActions;
window.AppActions = AppActions;
