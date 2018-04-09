import React, {Component} from 'react';
import Table from './Table.js';
import {DATA} from './data.js';
import './App.css'

class App extends Component {
    constructor() {
        super();
        this.state = {
            dataframe: DATA,
            columns: [

                {
                    'name': ' ',
                    'type': 'numeric',
                    'width': 30
                },

                {
                    'name': 'New York City',
//                    'width': '80px',
                    'type': 'numeric',
                    'style': {
                        'white-space': 'pre-line'
                    }
                },

                {
                    'name': 'Paris',
                    // 'width': '20%',
                    'type': 'numeric',
                    // 'hidden': true
                    'editable': false
                },

                {
                    'name': 'Montréal',
                    // 'width': '70%',
                    'type': 'numeric'
                },

                {
                    'name': 'Climate',
                    'type': 'dropdown',
                    'width': 200,
                    'options': [
                        'Humid',
                        'Wet',
                        'Snowy',
                        'Tropical Beaches'
                    ].map(i => ({label: i, value: i})),
                    'clearable': true
                },

            ],

            sort: [
                {
                    'column': 'Paris',
                    'direction': 'desc'
                }
            ],

            start_cell: [1, 0],
            end_cell: [1, 4],

            selected_cell: [
                // [0, 0],
                // [1, 0],
                // [0, 1],
                [1, 0], // [row, column]
                [1, 1],
                [1, 2],
                [1, 3],
                [1, 4]
            ],

            editable: true,
            is_focused: false,
            collapsable: true,
            expanded_rows: [],
            sortable: true,

            display_row_count: 50,
            display_tail_count: 5

        }
    }

    render() {
        return (
            <div>
                <Table
                    setProps={newProps => {
                        console.info('--->', newProps);
                        this.setState(newProps)
                    }}
                    {...this.state}
                />

                <div style={{'columnCount': 3}}>
                    <pre>{JSON.stringify(this.state, null, 2)}</pre>
                </div>

            </div>
        )
    }
}

class InputContainer extends Component {
    constructor() {
        super();
        this.state = {
            value: 3,
            isFocused: true
        }
    }

    render() {
        return <StatefulInput
            value={this.state.value}
            updateProps={
                newProps => this.setState(newProps)
            }
            isFocused={this.state.isFocused}
        />
    }
}

class StatefulInput extends Component {
    componentDidMount() {
        if (this.el && this.props.isFocused) {
            console.warn('componentDidMount - focus');
            this.el.focus();
        }
    }

    componentDidUpdate() {
        if (this.el && this.props.isFocused) {
            console.warn('componentDidUpdate - focus');
            this.el.focus();
        }
    }

    render() {
        return (
            <div style={{
                'padding': 50,
            }}
            >
                <button onClick={() => this.props.updateProps({
                    isFocused: false
                })}>
                    {'Unfocus'}
                </button>
                <button onClick={() => this.props.updateProps({
                    isFocused: true
                })}>
                    {'Focus'}
                </button>

                <div>
                    {`Focused: ${this.props.isFocused}`}
                </div>

                <input
                    className={`${
                        this.props.isFocused ?
                        'focused' : 'unfocused'
                    }`}
                    onChange={e => {
                        const newProps = {
                            value: e.target.value
                        };
                        if (!this.props.focused) {
                            newProps.isFocused = true;
                        }
                        this.props.updateProps(newProps);
                    }}

                    onClick={e => {
                        if(!this.props.isFocused) {
                            console.warn('click - preventDefault');
                            e.preventDefault();
                            this.props.updateProps({
                                isFocused: false
                            });
                        }
                        return e;
                    }}
                    onDoubleClick={e => {
                        if(!this.props.isFocused) {
                            console.warn('dblclick - preventDefault');
                            e.preventDefault();
                            this.props.updateProps({
                                isFocused: true
                            });
                        }
                        return e;
                    }}

                    type="text"
                    ref={el => this.el = el}
                    value={this.props.value}
                />
            </div>
        )
    }
}

export default App;
