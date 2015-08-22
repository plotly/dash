'use strict';

import React from 'react';
import AppActions from '../actions/AppActions';

var Dropdown = React.createClass({
    propTypes: {
        options: React.PropTypes.array.isRequired
    },
    handleChange: function(e) {
        return this.props.handleChange ? this.props.handleChange(e) : false;
    },
    render: function(){
        let options = this.props.options.map((v, i) => {
            return <option key={i} value={v.val}>{v.name}</option>
        });
        return (
            <div>
                <select onChange={this.handleChange}>
                    {options}
                </select>
            </div>
        );
    }
});

exports.Dropdown = Dropdown;
