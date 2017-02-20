import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import Playground from 'component-playground';
import {Dropdown, Graph, Input, RangeSlider, Slider} from '../src';

const DropdownExample = `
const properties = {
    id: 'my dropdown',
    disabled: false,
    multi: false,
    options: [
        {'label': 'Melons', 'value': 'melons', 'disabled': false},
        {'label': 'Apples', 'value': 'apples'},
        {'label': 'Oranges', 'value': 'oranges', 'disabled': true}
    ]
};

ReactDOM.render(<Dropdown {...properties}/>, mountNode);`

const GraphExample = `
const properties = {
    id: 'my graph',
    figure: {
        data: [
            {'x': [1, 2, 3], 'y': [4, 1, 6]}
        ],
        layout: {
            title: 'Graph Component'
        }
    }
};

ReactDOM.render(<Graph {...properties}/>, mountNode);`

const SliderExample = `
const properties = {
    className: 'my-slider',
    disabled: false,
    dots: false,
    id: 'my-slider',
    included: false,
    marks: {},
    min: -5,
    max: 5,
    step: 0.5,
    labels: {},
    value: -3,
    vertical: false
};

ReactDOM.render(<Slider {...properties}/>, mountNode);`

const RangeSliderExample = `
const properties = {
    allowCross: false,
    className: 'my-range-slider',
    count: 2,
    disabled: false,
    dots: false,
    id: 'my-range-slider',
    included: false,
    marks: {},
    min: -5,
    max: 5,
    pushable: false,
    step: 0.5,
    labels: {},
    value: [-3, 3],
    vertical: false
};

ReactDOM.render(<RangeSlider {...properties}/>, mountNode);`

const InputExample = `
const properties = {
    className: 'my-input-wrapper',
    id: 'my-input',
    placeholder: 'Enter a value....',
    style: {'color': 'skyblue'},
    value: 'Initial Value'
};

ReactDOM.render(<Input {...properties}/>, mountNode);`

const examples = [
    {name: 'Dropdown', code: DropdownExample},
    {name: 'Slider', code: SliderExample},
    {name: 'RangeSlider', code: RangeSliderExample},
    {name: 'Input', code: InputExample},
    {name: 'Graph', code: GraphExample}
];

class Demo extends Component {
    render() {
        return (
            <div style={{'fontFamily': 'Sans-Serif'}}>
                <h1>Dash Core Component Suite Demo</h1>

                {examples.map(example =>
                    <div>
                        <div style={{'marginBottom': 150}}>
                            <h3>{example.name}</h3>
                            <Playground
                                codeText={example.code}
                                scope={{React, ReactDOM, Dropdown, Graph, Input, RangeSlider, Slider}}
                                noRender={false}
                                theme={'xq-light'}
                            />
                        </div>
                        <hr style={{color: 'lightgrey'}}/>
                    </div>
                    )}
            </div>
        );
    }
}

export default Demo;
