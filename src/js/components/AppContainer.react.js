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
            // TODO: abstract this list of imported, user-defined components
            let componentLookup = {"Dropdown": Dropdown, "Slider": Slider, "PlotlyGraph": PlotlyGraph};
            let supportedReactHTMLElements = ['a', 'abbr', 'address', 'area', 'article', 'aside', 'audio', 'b', 'base', 'bdi', 'bdo', 'big', 'blockquote', 'body', 'br','button', 'canvas', 'caption', 'cite', 'code', 'col', 'colgroup', 'data', 'datalist', 'dd', 'del', 'details', 'dfn','dialog', 'div', 'dl', 'dt', 'em', 'embed', 'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5','h6', 'head', 'header', 'hr', 'html', 'i', 'iframe', 'img', 'input', 'ins', 'kbd', 'keygen', 'label', 'legend', 'li', 'link','main', 'map', 'mark', 'menu', 'menuitem', 'meta', 'meter', 'nav', 'noscript', 'object', 'ol', 'optgroup', 'option','output', 'p', 'param', 'picture', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby', 's', 'samp', 'script', 'section', 'select','small', 'source', 'span', 'strong', 'style', 'sub', 'summary', 'sup', 'table', 'tbody', 'td', 'textarea', 'tfoot', 'th','thead', 'time', 'title', 'tr', 'track', 'u', 'ul', 'var', 'video', 'wbr'];
            for(var i=0; i<supportedReactHTMLElements.length; i++) {
                componentLookup[supportedReactHTMLElements[i]] = supportedReactHTMLElements[i];
            }

            function jsonToJsx(obj) {
                return obj.map((v, i) => {
                    return React.createElement(
                        componentLookup[v.type],
                        React.__spread({}, v.props),
                        v.children && v.children.constructor === Array ? jsonToJsx(v.children) : v.children);
                });
            }
            let jsx = jsonToJsx([this.state.components]);
            return (
                <div>
                    {jsx}
                </div>
            )
        }
    }
});

module.exports = AppContainer;
