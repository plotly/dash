import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import * as R from 'ramda';
import {keys, merge} from 'ramda';

import Cell from './Cell';

export default class Header extends Component {
    render() {
        const {
            collapsable,
            columns
        } = this.props;
        const collapsableCell = (
            !collapsable ? null : (
            <th className='toggle-row'/>
        ));

        const headerCells = columns.map((c, i) => {
            const style = {};
            if (c.width) {
                style.width = c.width;
                style.maxWidth = c.width;
            }
            return (
                <th
                    style={style}
                    className={`${
                        i !== (columns.length - 1)
                        ? '' : 'cell--right-last'
                    }`}
                >
                    {c.name}
                </th>
            );
        });

        return (
            <thead>
                <tr>
                    {collapsableCell}
                    {headerCells}
                </tr>
            </thead>
        )
    }
}
