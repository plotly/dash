import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import * as R from 'ramda';
import {keys, merge} from 'ramda';

import Cell from './Cell';

export default class Header extends Component {
    constructor() {
        super();
        this.sort = this.sort.bind(this);
    }

    sort(colName) {
        const {dataframe, restore_index, setProps, sort} = this.props;

        let newSort = sort;

        let colSort = R.find(R.propEq('column', colName))(sort);
        if (colSort) {
            if (colSort.direction === 'desc') {
                colSort.direction = 'asc';
            } else if (colSort.direction === 'asc') {
                newSort = newSort.filter(
                    R.complement(R.propEq('column', colName)));
            }
        } else {
            newSort.push({
                column: colName,
                direction: 'desc'
            });
        }

        newSort = newSort.filter(R.complement(R.isEmpty));

        setProps({

            sort: newSort.filter(R.complement(R.not)),

            dataframe: R.sortWith(
                newSort.map(
                    s => s.direction === 'desc' ?
                    R.descend(R.prop(s.column)) :
                    R.ascend(R.prop(s.column))
                ),
                dataframe
            )

        })
    }

    render() {
        const {
            collapsable,
            columns,
            sortable,
            setProps,
            sort
        } = this.props;
        const collapsableCell = (
            !collapsable ? null : (
            <th className='expanded-row--empty-cell'/>
        ));

        const headerCells = columns.map((c, i) => {
            if (c.hidden) return null;
            const style = c.style || {
            };
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
                    {sortable ? (
                        <span
                            className='filter'
                            onClick={() => this.sort(c.name)}
                        >
                            {
                                R.find(R.propEq('column', c.name), sort) ?
                                (R.find(R.propEq('column', c.name), sort).direction
                                === 'desc' ? '↑' : '↓')
                                : '↕'
                            }
                        </span>
                    ) : ''}

                    <span>
                        {c.name}
                    </span>
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
