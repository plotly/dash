import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import Playground from 'component-playground';
import {
    Checklist,
    Dropdown,
    Graph,
    Input,
    RadioItems,
    RangeSlider,
    Slider,
    SyntaxHighlighter
} from '../src';

const SyntaxHighlighterExample = `

const properties = {
    language: 'python',
    theme: 'light',
    customStyle: {},
    codeTagProps: {},
    useInlineStyles: true,
    showLineNumbers: false,
    startingLineNumber: 0,
    lineNumberContainerStyle: {},
    lineNumberStyle: {},
    wrapLines: false,
    lineStyle: {},
    children: \`import Dash
dash.layout = Div([
    Graph(figure={'data': [{'x': [1, 2, 3]}]})
]);

def update_graph(lahlah):
	return dict(updates=lahlah)

<html>

</html>
function thisIsJavascript(test) {
    console.log({test: that});
}
\`
}

ReactDOM.render(<SyntaxHighlighter {...properties}/>, mountNode);
`

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

class Controller extends Component {
    constructor() {
        super();
        this.state = {};
    }

    render() {
        return (<div>
            <Graph
                valueChanged={(props) => {
                    this.setState({props});
                }}
                fireEvent={event => {
                    this.setState({event})
                }}
                {...properties}
            />
            <pre>{JSON.stringify(this.state, null, 2)}</pre>
        </div>);
    }
}

ReactDOM.render(<Controller/>, mountNode);`

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
    vertical: false
};


class Controller extends Component {
    constructor() {
        super();
        this.state = {
            value: [1, 2]
        };
    }

    render() {
        return (<RangeSlider
            valueChanged={(props) => {
                this.setState(props);
            }}
            fireEvent={event => console.warn(event)}
            value={this.state.value}
            {...properties}
        />);
    }
}

ReactDOM.render(<Controller/>, mountNode);`

const InputExample = `
const properties = {
    className: 'my-input-wrapper',
    id: 'my-input',
    placeholder: 'Enter a value....',
    style: {'color': 'skyblue'},
    value: 'Initial Value'
};

ReactDOM.render(<Input {...properties}/>, mountNode);`

const RadioExample = `
const properties = {
    id: 'my radios',
    labelStyle: {'display': 'block'},
    disabled: false,
    options: [
        {'label': 'Melons', 'value': 'melons', 'disabled': false},
        {'label': 'Apples', 'value': 'apples'},
        {'label': 'Oranges', 'value': 'oranges', 'disabled': true}
    ],
    value: 'apples'
};

ReactDOM.render(<RadioItems {...properties}/>, mountNode);`


const ChecklistExample = `
const properties = {
    id: 'my checklist',
    labelStyle: {'display': 'block'},
    disabled: false,
    options: [
        {'label': 'Melons', 'value': 'melons', 'disabled': false},
        {'label': 'Apples', 'value': 'apples'},
        {'label': 'Oranges', 'value': 'oranges', 'disabled': true}
    ]
};

class Controller extends Component {
    constructor() {
        super();
        this.state = {
            values: ['melons', 'apples']
        };
    }

    render() {
        return (<Checklist
            valueChanged={(props) => {
                this.setState(props);
            }}
            fireEvent={event => console.warn(event)}
            values={this.state.values}
            {...properties}
        />);
    }
}

ReactDOM.render(<Controller/>, mountNode);`



const examples = [
    {name: 'Graph', code: GraphExample},
    {name: 'SyntaxHighlighter', code: SyntaxHighlighterExample},
    {name: 'Radio', code: RadioExample},
    {name: 'Checklist', code: ChecklistExample},
    {name: 'Dropdown', code: DropdownExample},
    {name: 'Slider', code: SliderExample},
    {name: 'RangeSlider', code: RangeSliderExample},
    {name: 'Input', code: InputExample}
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
                                scope={{Component, React, ReactDOM, Checklist, Dropdown, Graph, Input, RadioItems, RangeSlider, Slider, SyntaxHighlighter}}
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
