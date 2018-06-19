/* eslint no-magic-numbers: 0 */
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Table} from '../lib';
import {mockData} from './data.js';
import Dropdown from 'react-select';
import TestFixtures from '../../tests/fixtures.json';
import {merge} from 'ramda';

const clone = o => JSON.parse(JSON.stringify(o));

class App extends Component {
    constructor() {
        super();
        this.state = {
            tableProps: {
                dataframe: clone(mockData.dataframe),
                columns: clone(mockData.columns),
                editable: true,
                row_selectable: 'multi',
                selected_rows: [5, 10, 15],
            },
            selectedFixture: null,
        };
    }

    render() {
        return (
            <div>
                <div>
                    <label>Load test case</label>
                    <Dropdown
                        options={TestFixtures.map(t => ({
                            label: t.name,
                            value: JSON.stringify(t.props),
                        }))}
                        onChange={e =>
                            this.setState({
                                tableProps: JSON.parse(e.value),
                                selectedFixture: e.value,
                            })
                        }
                        value={this.state.selectedFixture}
                    />
                </div>

                <hr />
                <label>test events:{'\u00A0\u00A0'}</label>
                <input type="text" />
                <input type="text" />
                <input type="text" />
                <hr />

                <Table
                    setProps={newProps => {
                        console.info('--->', newProps);
                        this.setState({
                            tableProps: merge(this.state.tableProps, newProps),
                        });
                    }}
                    {...this.state.tableProps}
                />
            </div>
        );
    }
}

App.propTypes = {
    value: PropTypes.any,
};

export default App;
