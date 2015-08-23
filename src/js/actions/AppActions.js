'use strict';

import AppConstants from '../constants/AppConstants';
import AppDispatcher from '../dispatchers/AppDispatcher';
import AppState from 'ampersand-app';
import request from 'request';

var AppActions = {
    setDropdownValue: function(dropdownValue, dropdownId) {
        AppDispatcher.dispatch({
            event: AppConstants.UPDATEDROPDOWNVALUE,
            dropdownValue: dropdownValue,
            dropdownId: dropdownId
        })
    }
};

module.exports = AppActions;
window.AppActions = AppActions;
