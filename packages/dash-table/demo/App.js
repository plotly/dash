/* eslint no-magic-numbers: 0 */
import * as R from 'ramda';
import React, {Component} from 'react';
import { DataTable } from 'dash-table';
import { memoizeOne } from 'core/memoizer';
import Logger from 'core/Logger';
import AppMode from './AppMode';

import './style.less';

class App extends Component {
    constructor() {
        super();

        this.state = AppMode;

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
        return (<DataTable
            setProps={this.setProps}
            {...this.state.tableProps}
        />);
    }
}

export default App;
