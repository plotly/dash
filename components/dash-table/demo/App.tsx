/* eslint no-magic-numbers: 0 */
import '@babel/polyfill/noConflict';
import * as R from 'ramda';
import React, {Component} from 'react';
import {DataTable} from 'dash-table/index';
import Environment from 'core/environment';
import {memoizeOne} from 'core/memoizer';
import Logger from 'core/Logger';
import AppState, {AppMode, AppFlavor} from './AppMode';

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
        const flavorParam = Environment.searchParams.get('flavor');
        const flavors = flavorParam ? flavorParam.split(';') : [];

        if (flavors.indexOf(AppFlavor.FilterNative) !== -1) {
            return (
                <div>
                    <button
                        className='clear-filters'
                        onClick={() => {
                            const tableProps = R.clone(this.state.tableProps);
                            tableProps.filter_query = '';

                            this.setState({tableProps});
                        }}
                    >
                        Clear Filter
                    </button>
                    <input
                        style={{width: '500px'}}
                        value={this.state.temp_filtering}
                        onChange={e =>
                            this.setState({temp_filtering: e.target.value})
                        }
                        onBlur={e => {
                            const tableProps = R.clone(this.state.tableProps);
                            tableProps.filter_query = e.target.value;

                            this.setState({tableProps});
                        }}
                    />
                </div>
            );
        } else if (mode === AppMode.TaleOfTwoTables) {
            if (!this.state.tableProps2) {
                this.setState({
                    tableProps2: R.clone(this.state.tableProps)
                });
            }

            const baseId = this.state.tableProps2 && this.state.tableProps2.id;

            return this.state.tableProps2 ? (
                <DataTable
                    {...this.state.tableProps2}
                    id={baseId ? 'table2' : baseId}
                />
            ) : null;
        }
    }

    render() {
        return (
            <div>
                {this.renderMode()}
                <DataTable
                    setProps={this.setProps()}
                    {...this.state.tableProps}
                />
            </div>
        );
    }

    private setProps = memoizeOne(() => {
        return (newProps: any) => {
            Logger.debug('--->', newProps);
            this.setState((prevState: any) => ({
                tableProps: R.mergeRight(prevState.tableProps, newProps)
            }));
        };
    });
}

export default App;
