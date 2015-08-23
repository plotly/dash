'use strict';

import React from 'react';
import AppStore from '../stores/AppStore';
import AppActions from '../actions/AppActions';
import appStoreMixin from './AppStore.mixin.js';
import {Dropdown, RadioButton, CheckBox, Slider} from './Controls.react.js'

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
                      handleChange={this.dropdownAndRadioChangeHandler}/>

            <div>Selected value: <b>{this.state.firstDropdown.selected}</b></div>

            <Dropdown id={this.state.secondDropdown.id}
                      options={this.state.secondDropdown.options}
                      handleChange={this.dropdownAndRadioChangeHandler}/>

            <div>Selected value: <b>{this.state.secondDropdown.selected}</b></div>

            <RadioButton id={this.state.firstRadio.id}
                         name={this.state.firstRadio.name}
                         options={this.state.firstRadio.options}
                         handleChange={this.dropdownAndRadioChangeHandler}/>

            <div>Selected value: <b>{this.state.firstRadio.selected}</b></div>

            <RadioButton id={this.state.secondRadio.id}
                         name={this.state.secondRadio.name}
                         options={this.state.secondRadio.options}
                         handleChange={this.dropdownAndRadioChangeHandler}/>

            <div>Selected value: <b>{this.state.secondRadio.selected}</b></div>

            <CheckBox   name={this.state.firstCheckbox.name}
                        options={this.state.firstCheckbox.options}/>

            {this.state.firstCheckbox.options.map((v, i) => {
                return (<div>{v.id}: {JSON.stringify(v.isChecked)}</div>)
            })}

            <label>
                <Slider min={this.state.firstSlider.min}
                        max={this.state.firstSlider.max}
                        step={this.state.firstSlider.step}
                        value={this.state.firstSlider.value}
                        id={this.state.firstSlider.id}/>
                <span>{this.state.firstSlider.value}</span>
            </label>

            <label>
                <Slider minDate={this.state.dateSlider.min}
                        maxDate={this.state.dateSlider.max}
                        stepMs={this.state.dateSlider.step}
                        id={this.state.dateSlider.id}/>
                <span>{this.state.dateSlider.value}</span>
            </label>

            </div>
        );
    }
});

module.exports = AppContainer;
