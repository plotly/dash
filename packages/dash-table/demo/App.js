/* eslint no-magic-numbers: 0 */
import * as R from 'ramda';
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import { Table } from 'dash-table';
import {mockData} from './data';
import { memoizeOne } from 'core/memoizer';
import Logger from 'core/Logger';

const clone = o => JSON.parse(JSON.stringify(o));


class App extends Component {
    constructor() {
        super();

        const data: any[] = clone(mockData.data);

        this.state = {
            filter: '',
            tableProps: {
                id: 'table',
                data,
                columns: clone(mockData.columns).map(col => R.merge(col, {
                    editable_name: true,
                    deletable: true
                //     type: 'dropdown'
                })),
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
                style_table: {
                    max_width: '1000px',
                    width: '1000px'
                },
                style_data_conditional: [
                    { max_width: 150, min_width: 150, width: 150 },
                    { if: { column_id: 'rows' }, max_width: 40, min_width: 40, width: 40 },
                    { if: { column_id: 'bbb' }, max_width: 200, min_width: 200, width: 200 },
                    { if: { column_id: 'bbb-readonly' }, max_width: 200, min_width: 200, width: 200 }
                ],
            }
        };

        const setProps = memoizeOne(() => {
            return newProps => {
                Logger.debug('--->', newProps);
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
