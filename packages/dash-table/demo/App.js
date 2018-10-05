/* eslint no-magic-numbers: 0 */
import * as R from 'ramda';
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import { Table } from 'dash-table';
import {mockData} from './data';
import { memoizeOne } from 'core/memoizer';

const clone = o => JSON.parse(JSON.stringify(o));


class App extends Component {
    constructor() {
        super();

        const dataframe: any[] = clone(mockData.dataframe);

        this.state = {
            filter: '',
            tableProps: {
                id: 'table',
                dataframe: dataframe,
                columns: clone(mockData.columns).map(col => R.merge(col, {
                    editable_name: true,
                    deletable: true,
                //     type: 'dropdown'
                })),
                content_style: 'grow',
                editable: true,
                sorting: true,
                n_fixed_rows: 4,
                n_fixed_columns: 2,
                merge_duplicate_headers: false,
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
                table_style: [
                    { selector: '.dash-spreadsheet.freeze-left', rule: 'width: 1000px; max-width: 1000px;' }
                ]
            }
        };

        const setProps = memoizeOne(() => {
            return newProps => {
                console.info('--->', newProps);
                this.setState(prevState => ({
                    tableProps: R.merge(prevState.tableProps, newProps)
                }));
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
            {...{ filtering: 'fe' }}
        />);
    }
}

App.propTypes = {
    value: PropTypes.any,
};

export default App;
