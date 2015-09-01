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
            // How to abstract this out?
            let componentLookup = {"dropdown": Dropdown, "slider": Slider, "graph": PlotlyGraph};
            let supportedReactHTMLElements = ['a', 'abbr', 'address', 'area', 'article', 'aside', 'audio', 'b', 'base', 'bdi', 'bdo', 'big', 'blockquote', 'body', 'br','button', 'canvas', 'caption', 'cite', 'code', 'col', 'colgroup', 'data', 'datalist', 'dd', 'del', 'details', 'dfn','dialog', 'div', 'dl', 'dt', 'em', 'embed', 'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5','h6', 'head', 'header', 'hr', 'html', 'i', 'iframe', 'img', 'input', 'ins', 'kbd', 'keygen', 'label', 'legend', 'li', 'link','main', 'map', 'mark', 'menu', 'menuitem', 'meta', 'meter', 'nav', 'noscript', 'object', 'ol', 'optgroup', 'option','output', 'p', 'param', 'picture', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby', 's', 'samp', 'script', 'section', 'select','small', 'source', 'span', 'strong', 'style', 'sub', 'summary', 'sup', 'table', 'tbody', 'td', 'textarea', 'tfoot', 'th','thead', 'time', 'title', 'tr', 'track', 'u', 'ul', 'var', 'video', 'wbr'];
            for(var i=0; i<supportedReactHTMLElements.length; i++) {
                componentLookup[supportedReactHTMLElements[i]] = supportedReactHTMLElements[i];
            }

            /*
            let order = ["w1", "br1", "x1", "br1", "y1", "br1", "z1", "g1", "s1"];
            let components = order.map((v, i) => {
                let component = this.state.components[v];
                console.log(component);
                return React.createElement(componentLookup[component.component], React.__spread({}, component)); //equiv: <Dropdown {...this.state.components[v]}/>
            });
            let inner = [React.createElement('h1', null, 'test h1'), React.createElement('h3', null, 'test h3')];
            return (
                <div>
                    { React.createElement('div', null, inner) }
                </div>
            );
            */

            /*
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
            */
        }
    }
});

module.exports = AppContainer;
