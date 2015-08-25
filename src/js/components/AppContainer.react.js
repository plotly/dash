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
            var heightStyle = {'height': this.state.graph.height};
            return (
                <div>
                    <div className="row">
                        <div className="two columns">
                            <label>
                                <Dropdown id={this.state.x.id} name={this.state.x.id} options={this.state.x.options}/>
                                <span>X</span>
                            </label>

                            <label>
                                <Dropdown id={this.state.y.id} name={this.state.y.id} options={this.state.y.options}/>
                                <span>Y</span>
                            </label>

                            <label>
                                <Dropdown id={this.state.color.id} name={this.state.color.id} options={this.state.color.options}/>
                                <span>Color</span>
                            </label>

                            <label>
                                <Dropdown id={this.state.rows.id} name={this.state.rows.id} options={this.state.rows.options}/>
                                <span>Rows</span>
                            </label>

                            <label>
                                <Dropdown id={this.state.size.id} name={this.state.size.id} options={this.state.size.options}/>
                                <span>Size</span>
                            </label>

                            <label>
                                <Dropdown id={this.state.slide.id} name={this.state.slide.id} options={this.state.slide.options}/>
                                <span>Slide</span>
                            </label>

                            <label>
                                <Slider min={this.state.slider.min} max={this.state.slider.max}
                                        step={this.state.slider.step} value={this.state.slider.value}
                                        id={this.state.slider.id}/>
                                <span>{this.state.slide.selected} ({this.state.slider.value})</span>
                            </label>
                        </div>

                        <div className="ten columns" style={heightStyle}>
                            <PlotlyGraph id={this.state.graph.id}
                                         figure={this.state.graph.figure}
                                         height={this.state.graph.height}/>
                        </div>
                    </div>
                </div>
            )

            // yikes!
            let output = [];
            let v;
            for(var i in this.state) {
                v = this.state[i];
                console.log(v.element);
                if(v.element === 'dropdown'){
                    console.log('case: dropdown');
                    output.push(<Dropdown id={this.state.x.id} key={i} id={v.id} options={v.options}/>);
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
