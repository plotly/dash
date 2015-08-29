'use strict';

import React from 'react';
import AppActions from '../actions/AppActions';
import {AppStore} from '../stores/AppStore';

var Dropdown = React.createClass({
    propTypes: {
        id: React.PropTypes.string.isRequired,
        options: React.PropTypes.array.isRequired,
        children: React.PropTypes.array.isRequired,
        selected: React.PropTypes.string.isRequired
    },

    handleChange: function(e) {
        // When does onChange fire?
        // Whenever value changes, props change, user selects?
        console.log('Dropdown', this.props.id, 'handleChange');
        let value = e.target.value;
        let id = e.target.id;
        AppActions.setSelectedValue(id, value);
    },

    _onChange: function() {},
    componentDidMount: function() {AppStore.addChangeListener(this._onChange);},
    componentWillUnmount: function() {AppStore.removeChangeListener(this._onChange);},

    componentWillReceiveProps: function(nextProps) {
        // Update this components state if it is outdated.
        // These "props" are actually the parent container's
        // state (eg <Dropdown id={this.state.1.id} .../>).
        // So, this will get called whenever the parent state changes
        // from the parent component's on change handlers.
        let outdated = AppStore.getState().meta.outdated;
        if(outdated.indexOf(this.props.id) > -1){
            AppActions.getDropdownState(this.props.id);
        }
    },

    render: function() {
        console.log('Dropdown', this.props.id, 'render');
        let options = this.props.options.map((v, i) => {
            return <option key={i} value={v.val}>{v.label}</option>
        });
        return (
            <select id={this.props.id} onChange={this.handleChange}>
                {options}
            </select>
        );
    }
});

var RadioButton = React.createClass({
    propTypes: {
        name: React.PropTypes.string.isRequired,
        options: React.PropTypes.array.isRequired,
    },

    handleChange: function(e) {
        let value = e.target.value;
        let id = e.target.id;
        AppActions.setSelectedValue(id, value);
    },

    render: function() {
        let options = this.props.options.map((v, i) => {
            return (
                <label>
                    <input  id={this.props.id}
                            onClick={this.handleChange}
                            type="radio"
                            name={this.props.name}
                            value={v.val}/>

                    <span>{v.label}</span>
                </label>)
        });

        return (
            <div>
                {options}
            </div>
        )
    }
});

var CheckBox = React.createClass({
    propTypes: {
        name: React.PropTypes.string.isRequired,
        options: React.PropTypes.array.isRequired
        // How to describe which propTypes are available in options? Declare a sub component?
    },

    handleChange: function(e) {
        let id = e.target.id;
        let isChecked = e.target.checked;
        AppActions.setCheckedValue(id, isChecked);
    },

    render: function(){
        let options = this.props.options.map((v, i) => {
            return (
                <label>
                    <input  id={v.id}
                            onClick={this.handleChange}
                            type="checkbox"
                            name={this.props.name}
                            isChecked={v.isChecked ? "checked": ""}/>
                    <span>{v.label}</span>
                </label>
            )
        })

        return (
            <div>
                {options}
            </div>
        )
    }
});

var Slider = React.createClass({
    propTypes: {
        min: React.PropTypes.number.isRequired,
        max: React.PropTypes.number.isRequired,
        step: React.PropTypes.number.isRequired,
        value: React.PropTypes.number.isRequired,
        id: React.PropTypes.string.isRequired
    },

    handleChange: function(e) {
        let id = e.target.id;
        let value = parseFloat(e.target.value, 10);
        AppActions.setValue(id, value);
        e.preventDefault();
    },

    render: function(){
        return (
            <input  type="range"
                    id={this.props.id}
                    min={this.props.min}
                    max={this.props.max}
                    step={this.props.step}
                    value={this.props.value}
                    onChange={this.handleChange}/>
        )
    }
});

var DateSlider = React.createClass({
    propTypes: {
        minDate: React.PropTypes.string.isRequired,
        maxDate: React.PropTypes.string.isRequired,
        stepMs: React.PropTypes.number.isRequired,
        id: React.PropTypes.string.isRequired
    },

    handleChange: function(e) {
        let id = e.target.id;
        let value = parseFloat(e.target.value, 10);
        value = (new Date(value)).toISOString();
        AppActions.setValue(id, value);
        e.preventDefault();
    },

    render: function(){
        return (
            <input  type="range"
                    id={this.props.id}
                    min={(new Date(this.props.minDate)).getTime()}
                    max={(new Date(this.props.maxDate)).getTime()}
                    step={this.props.stepMs}
                    onChange={this.handleChange}/>
        )
    }
});

var PlotlyGraph = React.createClass({
    propTypes: {
        figure: React.PropTypes.object.isRequired,
        id: React.PropTypes.string.isRequired,
        height: React.PropTypes.string.isRequired
    },

    // "Invoked once, only on the client (not on the server),
    // immediately after the initial rendering occurs."
    componentDidMount: function() {
        Plotly.newPlot(this.props.id,
                       this.props.figure.data,
                       this.props.figure.layout);
    },

    // "Invoked immediately after the component's updates are flushed to the DOM.
    // This method is not called for the initial render."
    componentDidUpdate: function() {
        Plotly.newPlot(this.props.id,
                       this.props.figure.data,
                       this.props.figure.layout);
    },

    render: function(){
        console.log('render ', this.props.height);
        var heightStyle = {'height': this.props.height};
        return (
            <div id={this.props.id}
                 width="100%"
                 style={heightStyle}>
            </div>
        );
    }
});

exports.Dropdown = Dropdown;
exports.RadioButton = RadioButton;
exports.CheckBox = CheckBox;
exports.Slider = Slider;
exports.DateSlider = DateSlider;
exports.PlotlyGraph = PlotlyGraph;
