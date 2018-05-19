/* eslint no-magic-numbers: 0 */
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import Table from '../lib';
import {mockData} from './data.js';

class App extends Component {
    constructor() {
        super();
        this.state = {
            dataframe: mockData.dataframe,
            n_fixed_columns: 0,
            n_fixed_rows: 0,
            merge_duplicate_headers: true,
            columns: mockData.columns,

            sort: [
                {
                    column: 'Paris',
                    direction: 'desc',
                },
            ],

            start_cell: [1, 0],
            end_cell: [1, 4],

            selected_cell: [[1, 0], [1, 1], [1, 2], [1, 3], [1, 4]],

            editable: true,
            is_focused: false,
            collapsable: false,
            expanded_rows: [],
            sortable: true,

            display_row_count: 25,
            display_tail_count: 5,

            width: 400,
            height: 500,
            table_style: {
                tableLayout: 'inherit',
            },
        };
    }

    render() {
        return (
            <div>
                <Table
                    setProps={newProps => {
                        console.info('--->', newProps);
                        this.setState(newProps);
                    }}
                    {...this.state}
                />
            </div>
        );
    }
}

App.propTypes = {
    value: PropTypes.any,
};

export default App;
