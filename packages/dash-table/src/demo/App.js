/* eslint no-magic-numbers: 0 */
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Table} from '../lib';
import {mockData} from './data.js';

const clone = o => JSON.parse(JSON.stringify(o));

class App extends Component {
    constructor() {
        super();
        this.state = {
            dataframe: clone(mockData.dataframe),
            columns: clone(mockData.columns),
            editable: true,
        };
    }

    render() {
        return (
            <div>
                <label>test events:{'\u00A0\u00A0'}</label>
                <input type="text" />
                <br />
                <br />
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
