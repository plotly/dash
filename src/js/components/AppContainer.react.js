'use strict';

import React from 'react';
import AppStore from '../stores/AppStore';
import AppActions from '../actions/AppActions';
import appStoreMixin from './AppStore.mixin.js';
import {Dropdown, RadioButton, CheckBox,
        Slider, DateSlider, PlotlyGraph} from './Controls.react.js'

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
        if(Object.keys(this.state).length === 0) {
            return <div>Loading...</div>
        } else {
            // yikes!
            let output = [];
            let v;
            for(var i in this.state) {
                v = this.state[i];
                console.log(v.element);
                if(v.element === 'dropdown'){
                    console.log('case: dropdown');
                    output.push(<Dropdown key={i} id={v.id} options={v.options}/>);
                } else if(v.element === 'checkbox'){
                    console.log('case: checkbox');
                    output.push(<CheckBox key={i} options={v.options} name={v.name}/>);
                } else if(v.element === 'slider') {
                    console.log('case: slider');
                    output.push(<Slider key={i} min={v.min} max={v.max} step={v.step} value={v.value} id={v.id}/>);
                } else if(v.element === 'dateSlider') {
                    console.log('case: dateSlider');
                    output.push(<DateSlider key={i} minDate={v.min} maxDate={v.max} stepMs={v.step} id={v.id}/>);
                } else if(v.element === 'radio') {
                    console.log('case: radio');
                    output.push(<RadioButton key={i} id={v.id} name={v.name} options={v.options}/>);
                } else if(v.element === 'PlotlyGraph') {
                    console.log('case: PlotlyGraph')
                    output.push(<PlotlyGraph key={i} id={v.id} figure={v.figure}/>);
                }
            }

            return (
                <div>
                    {output.map(function(r){
                        return r;
                    })}
                </div>
            );
        }
    }
});

module.exports = AppContainer;
