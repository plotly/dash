/* eslint no-magic-numbers: 0 */
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Table} from 'dash-table';
import {mockData} from './data';
import {merge} from 'ramda';
import { memoizeOne } from 'core/memoizer';

const clone = o => JSON.parse(JSON.stringify(o));

class App extends Component {
    constructor() {
        super();

        this.state = {
            filter: '',
            tableProps: {
                id: 'table',
                dataframe: clone(mockData.dataframe),
                columns: clone(mockData.columns).map(col => merge(col, {
                    editable_name: true,
                    deletable: true,
                //     type: 'dropdown'
                })),
                editable: true,
                // n_fixed_rows: 3,
                // n_fixed_columns: 2,
                sortable: false,
                sort: [],
                merge_duplicate_headers: true,
                row_deletable: true,
                row_selectable: 'single',
                column_static_dropdown: [
                    {
                        id: 'bbb',
                        dropdown: ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'].map(i => ({
                            label: i,
                            value: i,
                        }))
                    }
                ],
            }
        };

        const setProps = memoizeOne(() => {
            return newProps => {
                console.info('--->', newProps);
                this.setState({
                    tableProps: merge(this.state.tableProps, newProps),
                });
            };
        });

        Object.defineProperty(this, 'setProps', {
            get: () => setProps()
        });
    }

    render() {
        return (<Table
            setProps={this.setProps}
            {...this.state.tableProps}
            {...{ filtering: 'fe', filtering_settings: this.state.filter }}
        />);
    }
}

App.propTypes = {
    value: PropTypes.any,
};

export default App;
