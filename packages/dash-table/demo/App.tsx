/* eslint no-magic-numbers: 0 */
import * as R from 'ramda';
import React, {Component} from 'react';
import { DataTable } from 'dash-table/index';
import Environment from 'core/environment';
import { memoizeOne } from 'core/memoizer';
import Logger from 'core/Logger';
import AppState, { AppMode } from './AppMode';
import memoizerCache from 'core/cache/memoizer';

import './style.less';

class App extends Component<any, any> {
    constructor(props: any) {
        super(props);

        this.state = {
            ...AppState,
            temp_filtering: ''
        };
    }

    renderMode() {
        const mode = Environment.searchParams.get('mode');

        if (mode === AppMode.Filtering) {
            return (<div>
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
        } else if (mode === AppMode.TaleOfTwoTables) {
            const props: any = {};
            Object.entries(this.state.tableProps).forEach(([key, value]) => {
                props[key] = this.propCache.get(key)(value);
            });

            return (<DataTable
                {...props}
            />);
        }
    }

    render() {
        return (<div>
            {this.renderMode()}
            <DataTable
                setProps={this.setProps()}
                {...this.state.tableProps}
            />
        </div>);
    }

    private propCache = memoizerCache<[string]>()(R.clone);

    private setProps = memoizeOne(() => {
        return (newProps: any) => {
            Logger.debug('--->', newProps);
            this.setState((prevState: any) => ({
                tableProps: R.merge(prevState.tableProps, newProps)
            }));
        };
    });
}

export default App;
