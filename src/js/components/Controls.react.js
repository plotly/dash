'use strict';

import React from 'react';
import AppActions from '../actions/AppActions';

var Dropdown = React.createClass({
    propTypes: {
        id: React.PropTypes.string.isRequired,
        options: React.PropTypes.array.isRequired
    },

    handleChange: function(e) {
        return this.props.handleChange ? this.props.handleChange(e) : false;
    },

    render: function() {
        let options = this.props.options.map((v, i) => {
            return <option key={i} value={v.val}>{v.name}</option>
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
        options: React.PropTypes.array.isRequired
    },

    handleChange: function(e) {
        return this.props.handleChange ? this.props.handleChange(e): false;
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

                    <span>{v.name}</span>
                </label>)
        });

        return (
            <div>
                {options}
            </div>
        )
    }
})

exports.Dropdown = Dropdown;
exports.RadioButton = RadioButton;
