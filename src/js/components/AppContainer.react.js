'use strict';

import React from 'react';
import {AppStore} from '../stores/AppStore';
import AppActions from '../actions/AppActions';
import appStoreMixin from './AppStore.mixin.js';
import {Dropdown, RadioButton, CheckBox,
        Slider, DateSlider, PlotlyGraph, CodeBlock} from './Controls.react.js'

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
                        <div className="four columns">
                            <CodeBlock{...this.state.components.t1}/>
                        </div>

                        <div className="four columns">
                            <div className="row">
                                <Dropdown {...this.state.components.w1}/> W1
                                <Dropdown {...this.state.components.x1}/> X1
                                <Dropdown {...this.state.components.y1}/> Y1
                                <Dropdown {...this.state.components.z1}/> Z1
                            </div>
                            <div className="row">
                                <Dropdown {...this.state.components.w2}/> W2 - Depends on W1, X1
                                <Dropdown {...this.state.components.x2}/> X2 - Depends on X1, Y1
                                <Dropdown {...this.state.components.y2}/> Y2 - Depends on Z1
                            </div>

                            <div className="row">
                                <Dropdown {...this.state.components.w3}/> W3 - Depends on W2
                            </div>

                            <div className="row">
                                <Slider {...this.state.components.s1}/> S1 - Independent
                            </div>
                        </div>

                        <div className="four columns">
                            <div className="row">
                                <PlotlyGraph {...this.state.components.g1}/> G1 - Dependent on W1, W3, S1
                            </div>
                        </div>
                    </div>
                </div>
            )
        }
    }
});

module.exports = AppContainer;
