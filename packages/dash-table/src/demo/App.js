import React, {Component} from 'react';
import Table from '../lib';
import {DATA} from './data.js';

class App extends Component {
    constructor() {
        super();
        this.state = {
            dataframe: DATA,
            n_fixed_columns: 0,
            n_fixed_rows: 0,
            merge_duplicate_headers: true,
            columns: [

                {
                    'name': ' ',
                    'rows': ['City', 'Canada', 'Toronto'],
                    'type': 'numeric',
                    // 'width': 150,
                },

                {
                    'name': 'Montréal',
                    'rows': ['City', 'Canada', 'Montréal'],
                    'type': 'numeric',
                    'editable': false,
                    // 'width': 200
                },

                {
                    'name': 'New York City',
                    'rows': ['City', 'America', 'New York City'],
                    'type': 'numeric',
                    'style': {
                        'white-space': 'pre-line'
                    },
                    // 'width': 200
                },

                {
                    'name': 'Boston',
                    'rows': ['City', 'America', 'Boston'],
                    'type': 'numeric',
                    // 'width': 200
                },

                {
                    'name': 'Paris',
                    'rows': ['City', 'France', 'Paris'],
                    'type': 'numeric',
                    'editable': true,
                    // 'width': 200
                },

                {
                    'name': 'Climate',
                    'rows': ['', 'Weather', 'Climate'],
                    // 'type': 'dropdown',
                    'type': 'numeric',
                    'options': [
                        'Humid',
                        'Wet',
                        'Snowy',
                        'Tropical Beaches'
                    ].map(i => ({label: i, value: i})),
                    'clearable': true,
                    // 'width': 200
                },

                {
                    'name': 'Temperature',
                    'rows': ['', 'Weather', 'Temperature'],
                    'type': 'numeric',
                }

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
            collapsable: false,
            expanded_rows: [],
            sortable: true,

            display_row_count: 25,
            display_tail_count: 5,

            width: 500,
            height: 500,
            table_style: {
                'tableLayout': 'inherit',
            }

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
