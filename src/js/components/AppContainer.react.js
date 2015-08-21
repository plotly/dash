'use strict';

import React from 'react';
import AppStore from '../stores/AppStore';
import AppActions from '../actions/AppActions';
import appStoreMixin from './AppStore.mixin.js';
import {DropDown} from './DoubleD.react.js'

var AppContainer = React.createClass({
    getInitialState: function () {
        return this.getState();
    },

    mixins: [appStoreMixin],

    getState: function () {
        return {
            firstDropdown: AppStore.getFirstDropDown(),
            secondDropdown: AppStore.getSecondDropDown()
        };
    },

    setFirstD: function (e) {
        let dropdownValue = e.target.value;
        AppActions.setFirstD(dropdownValue);
    },

    _onChange: function () {
        // listens to store emittting events
        this.setState(this.getState());
    },

    render: function () {
        // this.state <- return value from getState
        let firstDropdown = this.state.firstDropdown;
        let secondDropdown = this.state.secondDropdown;
        return (
            <div>
            'Herro from react!'
            <br/>
            <DropDown options={firstDropdown} handleChange={this.setFirstD}/>
            <DropDown options={secondDropdown}/>
            </div>
        );
    }
});

module.exports = AppContainer;
