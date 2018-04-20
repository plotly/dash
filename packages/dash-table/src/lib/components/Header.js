import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import * as R from 'ramda';
import {keys, merge} from 'ramda';

import Cell from './Cell';
import computedStyles from './computedStyles';

export default class Header extends Component {
    constructor() {
        super();
        this.sort = this.sort.bind(this);
        this.renderHeaderCells = this.renderHeaderCells.bind(this);
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

    renderHeaderCells({labels, rowIsSortable, mergeCells}) {
        const {columns, sort} = this.props;
        const headerCells = [];

        let columnIndices;
        if (!mergeCells) {
            columnIndices = R.range(0, columns.length);
        } else {
            columnIndices = [0]; // [0, 5]
            let compareIndex = 0;
            labels.forEach((label, i) => {
                if (label === labels[compareIndex]) {
                    return;
                } else {
                    columnIndices.push(i);
                    compareIndex = i;
                }
            })
        }

        return columnIndices.map((i, j) => {
            const c = columns[i];
            if (c.hidden) return null;
            let style = c.style || {
            };
            if (c.width) {
                style.width = c.width;
                style.maxWidth = c.width;
                style.minWidth = c.width;
            }

            let colSpan;
            if (!mergeCells) {
                colSpan = 1;
            } else {
                if (i === R.last(columnIndices)) {
                    colSpan = labels.length - i;
                } else {
                    colSpan = columnIndices[j + 1] - i;
                }

            }

            style = R.merge(style, computedStyles.scroll.cell(this.props, i, 0))

            return (
                <th
                    colSpan={colSpan}
                    style={style}
                    className={`${
                        i !== (columns.length - 1)
                        ? '' : 'cell--right-last'
                    }`}
                >
                    {rowIsSortable ? (
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
                        {labels[i]}
                    </span>
                </th>
            );
        });

    }

    render() {
        const {
            collapsable,
            columns,
            sortable,
            setProps,
            sort,
            merge_duplicate_headers,
            n_fixed_columns
        } = this.props;

        const rowStyle = computedStyles.scroll.row(this.props, 0);

        let headerRows;

        const collapsableCell = (
            !collapsable ? null : (
            <th className='expanded-row--empty-cell'/>
        ));

        if (!R.has('rows', columns[0])) {
            headerRows = (
                <tr style={rowStyle}>
                    {collapsableCell}
                    {this.renderHeaderCells({
                        labels: R.pluck('name', columns),
                        rowIsSortable: sortable
                    })}
                </tr>
            )
        } else {
            headerRows = [];
            R.range(0, columns[0].rows.length).forEach(i => {
                headerRows.push(
                    <tr style={rowStyle}>
                        {collapsableCell}
                        {this.renderHeaderCells({
                            labels: R.pluck(
                                i,
                                R.pluck(
                                    'rows',
                                    columns
                                )
                            ),
                            rowIsSortable: (
                                sortable &&
                                (i + 1 ===
                                columns[i].rows.length)
                            ),
                            mergeCells: (
                                merge_duplicate_headers &&
                                (i + 1 !==
                                columns[i].rows.length)
                            )
                        })}
                    </tr>
                )
            });
        }

        return (
            <thead>
                {headerRows}
            </thead>
        )
    }
}
