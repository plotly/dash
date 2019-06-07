/* eslint no-magic-numbers: 0 */
import * as R from 'ramda';
import React, {Component} from 'react';
import { DataTable } from 'dash-table';
import Environment from 'core/environment';
import { memoizeOne } from 'core/memoizer';
import Logger from 'core/Logger';
import AppState, { AppMode } from './AppMode';

import './style.less';

class App extends Component {
    constructor() {
        super();

        this.state = AppState;
        this.state.temp_filtering = '';

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

    renderMode() {
        const mode = Environment.searchParams.get('mode');

        if (mode === AppMode.Filtering) {
            return (
                <div>
                    <button
                        className='clear-filters'
                        onClick={() => {
                            const tableProps = R.clone(this.state.tableProps);
                            tableProps.filter_query = '';

                            this.setState({ tableProps });
                        }}
                    >Clear Filter</button>
                    <input
                        style={{ width: '500px' }}
                        value={this.state.temp_filtering}
                        onChange={
                            e => this.setState({ temp_filtering: e.target.value })
                        }
                        onBlur={e => {
                            const tableProps = R.clone(this.state.tableProps);
                            tableProps.filter_query = e.target.value;

                            this.setState({ tableProps });
                        }} />
                </div>);
        }
    }

    render() {
        return (<div>
            {this.renderMode()}
            <DataTable
                setProps={this.setProps}
                {...this.state.tableProps}
            />
        </div>);
    }
}

export default App;
