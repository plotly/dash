'use strict';

import React from 'react';
import {AppStore} from '../stores/AppStore';
import AppActions from '../actions/AppActions';
import appStoreMixin from './AppStore.mixin.js';
import {Dropdown, RadioButton, CheckBox,
        Slider, DateSlider, PlotlyGraph} from './Controls.react.js'

var AppContainer = React.createClass({
    mixins: [appStoreMixin],

    getState: function () {
        // called from getInitialState, a React method.
        return AppStore.getState();
    },

    componentDidMount: function() {
        AppStore.addChangeListener(this._onChange);
    },

    componentWillUnmount: function() {
        AppStore.removeChangeListener(this._onChange);
    },

    // initialize this.state
    getInitialState: function () {
        return this.getState();
    },

    // update this.state
    _onChange: function () {
        this.setState(this.getState(), function(){});
    },

    render: function () {
        // this.state <- return value from getState
        if(Object.keys(this.state.components).length === 0) {
            return <div>Loading...</div>
        } else {
            return (
                <div>
                    <div className="row">
                        <Dropdown id={this.state.components.w1.id} options={this.state.components.w1.options} children={this.state.components.w1.children} dependson={this.state.components.w1.dependson}/> W1
                        <Dropdown id={this.state.components.x1.id} options={this.state.components.x1.options} children={this.state.components.x1.children} dependson={this.state.components.x1.dependson}/> X1
                        <Dropdown id={this.state.components.y1.id} options={this.state.components.y1.options} children={this.state.components.y1.children} dependson={this.state.components.y1.dependson}/> Y1
                        <Dropdown id={this.state.components.z1.id} options={this.state.components.z1.options} children={this.state.components.z1.children} dependson={this.state.components.z1.dependson}/> Z1
                    </div>
                    <div className="row">
                        <Dropdown id={this.state.components.w2.id} options={this.state.components.w2.options} children={this.state.components.w2.children} dependson={this.state.components.w2.dependson}/> W2 - Depends on W1, X1
                        <Dropdown id={this.state.components.x2.id} options={this.state.components.x2.options} children={this.state.components.x2.children} dependson={this.state.components.x2.dependson}/> X2 - Depends on X1, Y1
                        <Dropdown id={this.state.components.y2.id} options={this.state.components.y2.options} children={this.state.components.y2.children} dependson={this.state.components.y2.dependson}/> Y2 - Depends on Z1
                    </div>

                    <div className="row">
                        <Dropdown id={this.state.components.w3.id} options={this.state.components.w3.options} children={this.state.components.w3.children} dependson={this.state.components.w3.dependson}/> W3 - Depends on W2
                    </div>
                </div>
            )
        }
    }
});

module.exports = AppContainer;
