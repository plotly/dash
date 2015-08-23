'use strict';

import React from 'react';
import AppStore from '../stores/AppStore';
import AppActions from '../actions/AppActions';
import appStoreMixin from './AppStore.mixin.js';
import {Dropdown, RadioButton} from './Controls.react.js'

var AppContainer = React.createClass({
    getInitialState: function () {
        return this.getState();
    },

    mixins: [appStoreMixin],

    getState: function () {
        // magic?
        // the return of this function fills in this.state
        // why isn't this.state handled in AppStore?
        //
        // so really, this.state is whatever we want/need it to be
        return AppStore.getState();
    },

    dropdownChangeHandler: function(e) {
        let dropdownValue = e.target.value;
        let dropdownId = e.target.id;
        AppActions.setDropdownValue(dropdownValue, dropdownId);
    },

    _onChange: function () {
        // listens to AppStore emittting changes with AppStore.emitChange
        this.setState(this.getState());
    },

    render: function () {
        // this.state <- return value from getState

        return (
            <div>
            Herro from react!
            <br/>

            <Dropdown id={this.state.firstDropdown.id}
                      options={this.state.firstDropdown.options}
                      handleChange={this.dropdownChangeHandler}/>

            <div>Selected value: <b>{this.state.firstDropdown.selected}</b></div>

            <Dropdown id={this.state.secondDropdown.id}
                      options={this.state.secondDropdown.options}
                      handleChange={this.dropdownChangeHandler}/>

            <div>Selected value: <b>{this.state.secondDropdown.selected}</b></div>

            </div>
        );
    }
});

module.exports = AppContainer;
