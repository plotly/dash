/* eslint no-magic-numbers: 0 */
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Table} from 'dash-table';
import {mockData} from './data';
import Dropdown from 'react-select';
import TestFixtures from 'tests/python_fixtures/fixtures.json';
import {merge} from 'ramda';
import { memoizeOne } from 'core/memoizer';

const clone = o => JSON.parse(JSON.stringify(o));

class App extends Component {
    constructor() {
        super();

        this.onChange = this.onChange.bind(this);

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
            },
            selectedFixture: null,
        };

        const getOptions = memoizeOne(fixtures => {
            return fixtures.map(t => ({
                label: t.name,
                value: JSON.stringify(t.props),
            }));
        });

        const setProps = memoizeOne(() => {
            return newProps => {
                console.info('--->', newProps);
                this.setState({
                    tableProps: merge(this.state.tableProps, newProps),
                });
            };
        });

        Object.defineProperty(this, 'options', {
            get: () => getOptions(TestFixtures)
        });

        Object.defineProperty(this, 'setProps', {
            get: () => setProps()
        });
    }

    onChange(e) {
        this.setState({
            tableProps: JSON.parse(e.value),
            selectedFixture: e.value,
        })
    }

    render() {
        return (
            <div>
                {<div>
                    <label>Load test case</label>
                    <Dropdown
                        options={this.options}
                        onChange={this.onChange}
                        value={this.state.selectedFixture}
                    />
                </div>}

                <hr />
                <label>test events:{'\u00A0\u00A0'}</label>
                <input type="text" />
                <input type="text" />
                <input type="text" />
                <hr />

                <input
                    type='text'
                    value={this.state.filter}
                    onChange={e => this.setState({ filter: e.target.value })}
                />
                <Table
                    setProps={this.setProps}
                    {...this.state.tableProps}
                    {...{ filtering: 'fe', filtering_settings: this.state.filter }}
                />
            </div>
        );
    }
}

App.propTypes = {
    value: PropTypes.any,
};

export default App;
