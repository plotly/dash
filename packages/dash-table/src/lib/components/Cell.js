import React, {Component} from 'react';
import PropTypes from 'prop-types';
import * as R from 'ramda';
import Dropdown from 'react-select';

import {colIsEditable} from './derivedState';
import computedStyles from './computedStyles';

export default class Cell extends Component {
    constructor(props) {
        super(props);

        this.handleClick = this.handleClick.bind(this);
        this.handleDoubleClick = this.handleDoubleClick.bind(this);

        const {editable, columns, i} = props;
        this.state = {
            notEditable: !colIsEditable(editable, columns[i]),
        };
    }

    componentWillReceiveProps(nextProps) {
        const {editable, columns, i} = nextProps;
        this.setState({
            notEditable: !colIsEditable(editable, columns[i]),
        });
    }

    handleClick(e) {
        const {
            columns,
            setProps,
            idx,
            i,
            is_focused,
            isSelected,
            selected_cell,
        } = this.props;

        if (!is_focused) {
            e.preventDefault();
        }

        // don't update if already selected
        if (isSelected && selected_cell.length === 1) {
            return;
        }

        e.preventDefault();
        const cellLocation = [idx, i];
        const newProps = {
            is_focused: false,
            active_cell: cellLocation,
        };

        // visible col indices
        const vci = [];
        columns.forEach((c, i) => {
            if (!c.hidden) {
                vci.push(i);
            }
        });

        const selectedRows = R.uniq(R.pluck(0, selected_cell)).sort();
        const selectedCols = R.uniq(R.pluck(1, selected_cell)).sort();
        const minRow = selectedRows[0];
        const minCol = selectedCols[0];

        if (e.shiftKey) {
            newProps.selected_cell = R.xprod(
                R.range(
                    R.min(minRow, cellLocation[0]),
                    R.max(minRow, cellLocation[0]) + 1
                ),
                R.range(
                    R.min(minCol, cellLocation[1]),
                    R.max(minCol, cellLocation[1]) + 1
                )
            ).filter(c => R.contains(c[1], vci));
        } else {
            newProps.selected_cell = [cellLocation];
        }
        setProps(newProps);
    }

    handleDoubleClick(e) {
        const {setProps, idx, i, is_focused} = this.props;

        if (this._notEditable) {
            return;
        }

        if (!is_focused) {
            e.preventDefault();
            const newProps = {
                selected_cell: [[idx, i]],
                active_cell: [idx, i],
                is_focused: true,
            };
            setProps(newProps);
        }
    }

    componentDidUpdate() {
        const {active_cell, idx, i} = this.props;
        const isActive = active_cell[0] === idx && active_cell[1] === i;
        if (this.textInput) {
            if (isActive && this.props.is_focused) {
                this.textInput.focus();
            }
        }
    }

    borderStyle() {
        const {
            i: ci,
            idx: ri,
            columns,
            selected_cell,
            dataframe,
            collapsable,
            expanded_rows,
            active_cell,
        } = this.props;

        // visible col indices
        const vci = [];
        columns.forEach((c, i) => {
            if (!c.hidden) {
                vci.push(i);
            }
        });

        const isActive = active_cell[0] === ri && active_cell[1] === ci;

        // Left, Right, Top, Bottom
        const ACCENT = 'var(--accent)';
        const BORDER = 'var(--border)';

        const doLeft = (c, t) => `inset ${t}px 0px 0px 0px ${c}`;
        const doRight = (c, t) => `inset -${t}px 0px 0px 0px ${c}`;
        const doTop = (c, t) => `inset 0px ${t}px 0px 0px ${c}`;
        const doBottom = (c, t) => `inset 0px -${t}px 0px 0px ${c}`;

        const sortNumerical = R.sort((a, b) => a - b);
        const selectedRows = sortNumerical(R.uniq(R.pluck(0, selected_cell)));
        const selectedCols = sortNumerical(R.uniq(R.pluck(1, selected_cell)));

        const showInsideLeftEdge = isActive
            ? true
            : ci === R.head(selectedCols) && R.contains(ri, selectedRows);
        const showInsideTopEdge = isActive
            ? true
            : ri === R.head(selectedRows) && R.contains(ci, selectedCols);
        const showInsideRightEdge = isActive
            ? true
            : ci === R.last(selectedCols) && R.contains(ri, selectedRows);
        const showBottomEdge = isActive
            ? true
            : (ri === R.last(selectedRows) || false) &&
              R.contains(ci, selectedCols);

        const isRightmost = ci === R.last(vci);
        const isLeftmost = ci === R.head(vci);
        const isTopmost = ri === 0;
        const isBottommost = ri === dataframe.length - 1;
        const isNeighborToExpanded =
            collapsable && R.contains(ri, expanded_rows) && ci === vci[0];
        const isAboveExpanded = collapsable && R.contains(ri, expanded_rows);
        const isSelectedColumn = R.contains(ci, selectedCols);
        const isSelectedRow = R.contains(ri, selectedRows);

        // rules are applied in the order that they are supplied
        const boxShadowRules = [
            showInsideLeftEdge || isNeighborToExpanded
                ? doLeft(ACCENT, isActive ? 2 : 1)
                : null,
            showInsideTopEdge ? doTop(ACCENT, isActive ? 2 : 1) : null,
            showBottomEdge ? doBottom(ACCENT, isActive ? 2 : 1) : null,
            showInsideRightEdge ? doRight(ACCENT, isActive ? 2 : 1) : null,
            isSelectedColumn && isTopmost ? doTop(ACCENT, 1) : null,
            isSelectedRow && isLeftmost ? doLeft(ACCENT, 1) : null,

            doLeft(BORDER, 1),
            doTop(BORDER, 1),

            isBottommost || isAboveExpanded ? doBottom(BORDER, 1) : null,
            isRightmost ? doRight(BORDER, 1) : null,
        ].filter(R.complement(R.not));

        const sortedBoxRules = R.sort(
            a => (R.contains(ACCENT, a) ? -1 : 1),
            boxShadowRules
        );

        const style = {
            boxShadow: `${sortedBoxRules.join(', ')}`,
        };

        return style;
    }

    borderSquares() {
        const {i: ci, idx: ri, columns, selected_cell} = this.props;

        // visible col indices
        const vci = [];
        columns.forEach((c, i) => {
            if (!c.hidden) {
                vci.push(i);
            }
        });

        const sortNumerical = R.sort((a, b) => a - b);
        const selectedRows = sortNumerical(R.uniq(R.pluck(0, selected_cell)));
        const selectedCols = sortNumerical(R.uniq(R.pluck(1, selected_cell)));

        const isRight = ci === R.last(selectedCols) + 1;
        const isBelow = ri === R.last(selectedRows) + 1;

        const className = isRight && isBelow ? 'bottom-right' : '';
        if (!className) {
            return null;
        }
        return (
            <div className={`selected-square selected-square-${className}`} />
        );
    }

    fixedColumnStyle() {}

    render() {
        const {
            c,
            i,
            idx,
            isSelected,
            value,
            setProps,
            dataframe,
            is_focused,
            columns,
            selected_cell,
            active_cell,
        } = this.props;

        const {notEditable} = this.state;
        const isActive = active_cell[0] === idx && active_cell[1] === i;

        let innerCell;
        if (
            !R.has('type', columns[i]) ||
            R.contains(columns[i].type, ['numeric', 'text'])
        ) {
            innerCell = (
                <input
                    id={`${c.id}-${idx}`}
                    type="text"
                    value={value}
                    onClick={this.handleClick}
                    onDoubleClick={this.handleDoubleClick}
                    ref={el => (this.textInput = el)}
                    onChange={e => {
                        if (notEditable) {
                            return;
                        }
                        if (isSelected) {
                            const newDataframe = R.set(
                                R.lensPath([idx, c.id]),
                                e.target.value,
                                dataframe
                            );
                            setProps({
                                is_focused: true,
                                dataframe: newDataframe,
                            });
                        }
                    }}
                    onPaste={e => {
                        if (!(isSelected && is_focused)) {
                            e.preventDefault();
                        }
                    }}
                    className={
                        (isActive ? 'input-active ' : '') +
                        (is_focused && isActive ? 'focused ' : 'unfocused ')
                    }
                />
            );
        } else if (columns[i].type === 'dropdown') {
            innerCell = (
                <Dropdown
                    placeholder={''}
                    options={columns[i].options}
                    onChange={newOption => {
                        const newDataframe = R.set(
                            R.lensPath([idx, c.id]),
                            newOption ? newOption.value : newOption,
                            dataframe
                        );
                        setProps({dataframe: newDataframe});
                    }}
                    clearable={columns[i].clearable}
                    value={value}
                />
            );
        } else {
            innerCell = value;
        }

        return (
            <td
                style={R.merge(
                    this.borderStyle(),
                    computedStyles.scroll.cell(this.props, i)
                )}
                className={
                    (isSelected && selected_cell.length > 1
                        ? 'cell--selected '
                        : '') +
                    (is_focused && isActive ? 'focused ' : '') +
                    (notEditable ? 'cell--uneditable ' : '')
                }
            >
                {innerCell}

                {this.borderSquares()}
            </td>
        );
    }
}

Cell.propTypes = {
    c: PropTypes.any,
    collapsable: PropTypes.any,
    columns: PropTypes.any,
    dataframe: PropTypes.any,
    editable: PropTypes.any,
    expanded_rows: PropTypes.any,
    i: PropTypes.any,
    idx: PropTypes.any,
    isSelected: PropTypes.any,
    is_focused: PropTypes.any,
    selected_cell: PropTypes.any,
    setProps: PropTypes.any,
    value: PropTypes.any,
    active_cell: PropTypes.array,
};
