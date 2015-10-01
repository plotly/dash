'use strict';

import React from 'react';
import AppActions from '../actions/AppActions';
import {AppStore} from '../stores/AppStore';

var CodeBlock = React.createClass({
    mixins: [UpdateIfOutdatedMixin],

    propTypes: {
        id: React.PropTypes.string.isRequired,
        codeblock: React.PropTypes.string.isRequired
    },

    render: function() {
        return <pre id={this.props.id}>{this.props.codeblock}</pre>
    }
});

var Dropdown = React.createClass({
    propTypes: {
        id: React.PropTypes.string.isRequired,
        options: React.PropTypes.shape({
            'label': React.PropTypes.string.isRequired,
            'val': React.PropTypes.string.isRequired
        }).isRequired,
        selected: React.PropTypes.string
    },

    handleChange: function(e) {
        console.log('Dropdown', this.props.id, 'handleChange');
        let value = e.target.value;
        let id = e.target.id;
        AppActions.setSelectedValue(id, value);
    },

    render: function() {
        console.log('Dropdown', this.props.id, 'render');
        let options = this.props.options.map((v, i) => {
            let selected = (this.props.selected ? "selected" : null);

            return <option key={i} value={v.val}>{v.label}</option>
        });
        return (
            <select value={this.props.selected} id={this.props.id} onChange={this.handleChange}>
                {options}
            </select>
        );
    }
});

var Slider = React.createClass({
    propTypes: {
        min: React.PropTypes.number.isRequired,
        max: React.PropTypes.number.isRequired,
        step: React.PropTypes.number.isRequired,
        value: React.PropTypes.number.isRequired,
        id: React.PropTypes.string.isRequired,
        label: React.PropTypes.bool
    },

    getDefaultProps: function() {
        return {
            label: true
        }
    },

    handleChange: function(e) {
        let id = e.target.id;
        let value = parseFloat(e.target.value, 10);
        AppActions.setValue(id, value);
        e.preventDefault();
    },

    render: function(){
        let slider = <input  type="range"
                    id={this.props.id}
                    min={this.props.min}
                    max={this.props.max}
                    step={this.props.step}
                    value={this.props.value}
                    onChange={this.handleChange}/>;
        if(this.props.label) {
            return (
                <div>
                    {slider}
                    <span>{this.props.value}</span>
                </div>
            );
        } else {
            return {slider};
        }
    }

});

var RadioButton = React.createClass({
    propTypes: {
        name: React.PropTypes.string.isRequired,
        options: React.PropTypes.shape({
            value: React.PropTypes.string.isRequired,
            label: React.PropTypes.string.isRequired
        }).isRequired
    },

    handleChange: function(e) {
        AppActions.setSelectedValue(e.target.id, e.target.value);
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
    // need to consolidate the checkbox into an object with a parent id

    propTypes: {
        name: React.PropTypes.string.isRequired,
        options: React.PropTypes.shape({
            isChecked: React.PropTypes.bool.isRequired,
            id: React.PropTypes.bool.isRequired,
            label: React.PropTypes.string.isRequired
        }).isRequired
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

// finish this one later - need to consolidate value with valueDate etc
var DateSlider = React.createClass({
    propTypes: {
        id: React.PropTypes.string.isRequired,
        minDate: React.PropTypes.string.isRequired,
        maxDate: React.PropTypes.string.isRequired,
        stepMs: React.PropTypes.number.isRequired,
        valueDate: React.PropTypes.string,
        label: React.PropTypes.bool
    },

    getDefaultProps: function() {
        return {label: true};
    },

    handleChange: function(e) {
        let id = e.target.id;
        let value = parseFloat(e.target.value, 10);
        value = (new Date(value)).toISOString();
        AppActions.setValue(id, value);
        e.preventDefault();
    },

    render: function() {
        let slider = <input  type="range"
            id={this.props.id}
            min={(new Date(this.props.minDate)).getTime()}
            max={(new Date(this.props.maxDate)).getTime()}
            step={this.props.stepMs}
            onChange={this.handleChange}/>;

        if(this.props.label) {
            return (
                <div>
                    {slider}
                    <span>{this.props.value}</span>
                </div>
            );
        } else {
            return {slider};
        }
    }
});

var PlotlyGraph = React.createClass({
    propTypes: {
        figure: React.PropTypes.shape({
            data: React.PropTypes.array,
            layout: React.PropTypes.object
        }),
        id: React.PropTypes.string.isRequired,
        height: React.PropTypes.string
    },

    getDefaultProps: function() {
        return {
            height: '600px',
            figure: {data: [], layout: {}}
        }
    },

    _plot: function(){
        Plotly.newPlot(this.props.id,
                       'figure' in this.props && this.props.figure && 'data' in this.props.figure ? this.props.figure.data : [],
                       'figure' in this.props && this.props.figure && 'layout' in this.props.figure ? this.props.figure.layout: {});
    },

    // "Invoked once, only on the client (not on the server),
    // immediately after the initial rendering occurs."
    componentDidMount: function() {
        console.log('newPlot');
        this._plot();
    },

    // "Invoked immediately after the component's updates are flushed to the DOM.
    // This method is not called for the initial render."
    componentDidUpdate: function() {
        console.log('newPlot');
        this._plot();
    },

    render: function(){
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
exports.CodeBlock = CodeBlock;
