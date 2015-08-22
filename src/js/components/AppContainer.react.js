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
        return {
            firstDropdown: AppStore.getFirstDropdown(),
            firstDropdownSelection: AppStore.getFirstDropdownSelection(),

            firstRadio: AppStore.getFirstRadio(),
            firstRadioSelection: AppStore.getFirstRadioSelection()
        };
    },

    firstDropdownChangeHandler: function(e) {
        let dropdownValue = e.target.value;
        AppActions.setFirstDropdownValue(dropdownValue);
    },

    firstRadioButtonChangeHandler: function(e) {
        console.log(e);
        let radioButtonValue = e.target.value;
        AppActions.setFirstRadioButtonValue(radioButtonValue);
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
            <Dropdown options={this.state.firstDropdown}
                      handleChange={this.firstDropdownChangeHandler}/>

            <div>Selected value: <b>{this.state.firstDropdownSelection}</b></div>

            <RadioButton name='daysoftheweek'
                         options={this.state.firstRadio}
                         handleChange={this.firstRadioButtonChangeHandler}/>

            <div>Selected value: <b>{this.state.firstRadioSelection}</b></div>

            </div>
        );
    }
});

module.exports = AppContainer;
