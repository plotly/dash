import React, {Component} from 'react';
import PropTypes from 'prop-types';
import * as R from 'ramda';
import computedStyles from './computedStyles';

const getColLength = c => (Array.isArray(c.name) ? c.name.length : 1);
const getColNameAt = (c, i) => (Array.isArray(c.name) ? c.name[i] : '');

export default class Header extends Component {
    constructor() {
        super();
        this.sort = this.sort.bind(this);
        this.renderHeaderCells = this.renderHeaderCells.bind(this);
    }

    sort(colId) {
        const {dataframe, setProps, sort} = this.props;

        let newSort = sort;
        const colSort = R.find(R.propEq('column', colId))(sort);

        if (colSort) {
            if (colSort.direction === 'desc') {
                colSort.direction = 'asc';
            } else if (colSort.direction === 'asc') {
                newSort = newSort.filter(
                    R.complement(R.propEq('column', colId))
                );
            }
        } else {
            newSort.push({
                column: colId,
                direction: 'desc',
            });
        }

        newSort = newSort.filter(R.complement(R.isEmpty));

        setProps({
            sort: newSort.filter(R.complement(R.not)),

            dataframe: R.sortWith(
                newSort.map(
                    s =>
                        s.direction === 'desc'
                            ? R.descend(R.prop(s.column))
                            : R.ascend(R.prop(s.column))
                ),
                dataframe
            ),
        });
    }

    renderHeaderCells({labels, rowIsSortable, mergeCells}) {
        const {columns, sort} = this.props;
        let columnIndices;
        if (!mergeCells) {
            columnIndices = R.range(0, columns.length);
        } else {
            columnIndices = [0];
            let compareIndex = 0;
            labels.forEach((label, i) => {
                if (label === labels[compareIndex]) {
                    return;
                }
                columnIndices.push(i);
                compareIndex = i;
            });
        }

        return columnIndices.map((i, j) => {
            const c = columns[i];
            if (c.hidden) {
                return null;
            }
            let style = R.merge({}, c.style) || {};

            let colSpan;
            if (!mergeCells) {
                colSpan = 1;
            } else {
                const nHiddenColumns = (
                    R.slice(i, columnIndices[j+1] || Infinity, columns)
                     .filter(R.propEq('hidden', true))
                     .length);
                if (i === R.last(columnIndices)) {
                    colSpan = labels.length - i - nHiddenColumns;
                } else {
                    colSpan = columnIndices[j + 1] - i - nHiddenColumns;
                }
            }

            if (c.width && colSpan === 1) {
                style.width = c.width;
                style.maxWidth = c.width;
                style.minWidth = c.width;
            }

            style = R.merge(
                style,
                computedStyles.scroll.cell(this.props, i, 0)
            );

            if (colSpan !== 1) {
                const widths = R.range(
                    i,
                    R.min(i + colSpan, labels.length)
                ).map(
                    k =>
                        R.type(columns[k].width) === 'Number'
                            ? `${columns[k].width}px`
                            : columns[k].width
                );
                style.width = `calc(${widths.join(' + ')})`;
                style.maxWidth = style.width;
                style.minWidth = style.width;
            }

            return (
                <th
                    colSpan={colSpan}
                    style={style}
                    className={`${
                        i === columns.length - 1 || i === R.last(columnIndices)
                            ? 'cell--right-last'
                            : ''
                    }`}
                >
                    {rowIsSortable ? (
                        <span
                            className="filter"
                            onClick={() => this.sort(c.id)}
                        >
                            {R.find(R.propEq('column', c.id), sort)
                                ? R.find(R.propEq('column', c.id), sort)
                                      .direction === 'desc'
                                    ? '↑'
                                    : '↓'
                                : '↕'}
                        </span>
                    ) : (
                        ''
                    )}

                    <span>{labels[i]}</span>
                </th>
            );
        });
    }

    render() {
        const {
            collapsable,
            columns,
            sortable,
            merge_duplicate_headers,
            row_deletable,
            row_selectable
        } = this.props;

        let headerRows;

        const collapsableCell = !collapsable ? null : (
            <th className="expanded-row--empty-cell" />
        );
        const selectableCell = !row_selectable ? null : (
            <th className="expanded-row--empty-cell"
                style={{'width': 30}}
             />
        );
        const deletableCell = !row_deletable ? null : (
            <th className="expanded-row--empty-cell"
                style={{'width': 30}}
             />
        )

        // TODO calculate in lifecycle function
        const headerDepth = Math.max.apply(Math, columns.map(getColLength));
        if (headerDepth === 1) {
            const rowStyle = computedStyles.scroll.row(this.props, 0);
            headerRows = (
                <tr style={rowStyle}>
                    {collapsableCell}
                    {selectableCell}
                    {this.renderHeaderCells({
                        labels: R.pluck('name', columns),
                        rowIsSortable: sortable,
                    })}
                </tr>
            );
        } else {
            headerRows = [];
            R.range(0, headerDepth).forEach(i => {
                const rowStyle = computedStyles.scroll.row(this.props, i);
                headerRows.push(
                    <tr style={rowStyle}>
                        {deletableCell}
                        {collapsableCell}
                        {selectableCell}
                        {this.renderHeaderCells({
                            labels: columns.map(
                                c =>
                                    R.isNil(c.name) && i === headerDepth - 1
                                        ? c.id
                                        : getColNameAt(c, i)
                            ),
                            rowIsSortable: sortable && i + 1 === headerDepth,
                            mergeCells:
                                merge_duplicate_headers &&
                                i + 1 !== headerDepth,
                        })}
                    </tr>
                );
            });
        }

        return <thead>{headerRows}</thead>;
    }
}

Header.propTypes = {
    collapsable: PropTypes.any,
    columns: PropTypes.any,
    sortable: PropTypes.any,
    merge_duplicate_headers: PropTypes.any,
    dataframe: PropTypes.any,
    setProps: PropTypes.any,
    sort: PropTypes.any,
    row_deletable: PropTypes.bool,
    row_selectable: PropTypes.any
};
