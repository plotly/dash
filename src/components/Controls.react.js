'use strict';

import React from 'react';
import AppActions from '../actions/AppActions';
import {AppStore} from '../stores/AppStore';


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
                    <label><span>{this.props.label}</span></label>
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
        id: React.PropTypes.string.isRequired,
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
                            value={v.value}/>

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


var CheckList = React.createClass({
    propTypes: {
        id: React.PropTypes.string.isRequired,
        options: React.PropTypes.arrayOf(
            React.PropTypes.shape({
                checked: React.PropTypes.bool.isRequired,
                // TODO: consolidate this with Dropdown's "values"
                id: React.PropTypes.bool.isRequired,
                label: React.PropTypes.string.isRequired,
                // TODO: abstract this to "style"?
                hidden: React.PropTypes.bool
            })
        ).isRequired
    },

    handleChange: function(e) {
        let checkboxid = e.target.id;
        let isChecked = e.target.checked;
        AppActions.setCheckedValue(this.props.id, checkboxid, isChecked);
    },

    render: function() {
        let options = this.props.options.map((v, i) => {
            let style = {};
            if(v.hidden) {
                style.display = 'none';
            }
            return (
                <label key={v.id} style={style}>
                    <input  id={v.id}
                            onClick={this.handleChange}
                            type="checkbox"
                            name={this.props.name}
                            key={v.id}
                            checked={v.checked ? "checked": ""}/>
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

var TextInput = React.createClass({
    propTypes: {
        id: React.PropTypes.string.isRequired,
        label: React.PropTypes.string.isRequired,
        value: React.PropTypes.string.isRequired,
        placeholder: React.PropTypes.string.isRequired,
        labelstyle: React.PropTypes.shape.isRequired, // surely there's a better way
    },

    updateInput: function(e) {
        AppActions.setValue(e.target.id, e.target.value);
    },

    render: function() {
        let label = (<label style={this.props.labelstyle}
                        className="chart-title">{this.props.label}</label>)

        return (
        <div style={{display: "inline-block", marginBottom: '10px'}}>
            {label}
            <input
                id={this.props.id}
                onChange={this.updateInput}
                type="text"
                placeholder={this.props.placeholder}
                value={this.props.value}/>
        </div>);
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
        height: React.PropTypes.string,
        width: React.PropTypes.string,
        bindHover: React.PropTypes.bool,
        hover: React.PropTypes.object,
        bindClick: React.PropTypes.bool,
        click: React.PropTypes.object
    },

    getDefaultProps: function() {
        return {
            height: '600px',
            width: '100%',
            figure: {data: [], layout: {}}
        }
    },

    _plot: function(){
        Plotly.newPlot(this.props.id,
                       'figure' in this.props && this.props.figure && 'data' in this.props.figure ? this.props.figure.data : [],
                       'figure' in this.props && this.props.figure && 'layout' in this.props.figure ? this.props.figure.layout: {});
    },

    _filterEventData: function(plotlyEventData) {
        var filteredEventData = {'points': []};
        // todo - a bunch more probably
        var validKeys = ['x', 'y', 'z', 'labels', 'values', 'pointNumber', 'curveNumber'];
        for(var i=0; i<plotlyEventData.points.length; i++) {
            filteredEventData.points.push({});
            for(var j=0; j<validKeys.length; j++) {
                if(validKeys[j] in plotlyEventData.points[i]) {
                    filteredEventData.points[filteredEventData.points.length-1][validKeys[j]] = plotlyEventData.points[i][validKeys[j]];
                }
            }
        }
        return filteredEventData;
    },

    // "Invoked once, only on the client (not on the server),
    // immediately after the initial rendering occurs."
    componentDidMount: function() {
        var that = this;
        this._plot();
        this.setState({lastFigure: this.props.figure});

        if(this.props.bindHover) {
            console.warn('binding Hover to ', this.props.id);
            $('#'+this.props.id).bind('plotly_hover', function(event, data){
                data = that._filterEventData(data);
                console.warn('hover - ', data);
                AppActions.setKey(that.props.id, 'hover', data);
            });
        }

        if(this.props.bindClick) {
            console.warn('binding Click to ', this.props.id);
            $('#'+this.props.id).bind('plotly_click', function(event, data){
                data = that._filterEventData(data)
                console.warn('click - ', data);
                AppActions.setKey(that.props.id, 'click', data);
            });
        }
    },

    shouldComponentUpdate: function(nextProps, nextState) {
        return JSON.stringify(this.props.figure) !== JSON.stringify(nextProps.figure);
    },

    // "Invoked immediately after the component's updates are flushed to the DOM.
    // This method is not called for the initial render."
    componentDidUpdate: function() {
        console.log('newPlot');
        this._plot();
    },

    render: function(){
        var style = {'height': this.props.height, 'width': this.props.width};
        return (
            <div id={this.props.id}
                 style={style}>
            </div>
        );
    }
});

exports.Dropdown = Dropdown;
exports.RadioButton = RadioButton;
exports.CheckList = CheckList;
exports.Slider = Slider;
exports.DateSlider = DateSlider;
exports.PlotlyGraph = PlotlyGraph;
exports.TextInput = TextInput;
