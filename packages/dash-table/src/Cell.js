import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import * as R from 'ramda';
import {keys, merge} from 'ramda';

export default class Cell extends Component {
    constructor(props) {
        super(props);

        this.handleClick = this.handleClick.bind(this);
        this.handleDoubleClick = this.handleDoubleClick.bind(this);
        this.borderStyle = this.borderStyle.bind(this);
        this.borderSquares = this.borderSquares.bind(this);
    }

    handleClick(e) {
        const {
            columns,
            setProps,
            start_cell,
            idx,
            i,
            is_focused,
            isSelected,
            selected_cell
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
        let newSelectedCell;
        const newProps = {
            is_focused: false,
            end_cell: cellLocation
        };

        const vci = [];  // visible col indices
        columns.forEach((c, i) => {if(!c.hidden) vci.push(i)});

        if (e.shiftKey) {
            newProps.selected_cell = R.xprod(
                R.range(
                    R.min(start_cell[0], cellLocation[0]),
                    R.max(start_cell[0], cellLocation[0]) + 1
                ),
                R.range(
                    R.min(start_cell[1], cellLocation[1]),
                    R.max(start_cell[1], cellLocation[1]) + 1
                )
            ).filter(c => R.contains(c[1], vci));
        } else {
            newProps.selected_cell = [cellLocation];
            newProps.start_cell = cellLocation;
        }
        setProps(newProps);

    }

    handleDoubleClick(e) {
        const {setProps, idx, i, is_focused, isSelected} = this.props;

        if (!is_focused) {
            e.preventDefault();
            const newProps = {
                selected_cell: [[idx, i]],
                is_focused: true
            }
            setProps(newProps);
        }
    }

    componentDidUpdate() {
        if (this.textInput) {
            if (this.props.isSelected &&
                this.props.is_focused
            ) {
                console.warn(`focus: [${this.props.c.name}, ${this.props.i}]`);
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
            expanded_rows
        } = this.props;

        const vci = [];  // visible col indices
        columns.forEach((c, i) => {if(!c.hidden) vci.push(i)});

        // Left, Right, Top, Bottom
        const Accent = 'var(--accent)';
        const Hidden = 'transparent';
        const Border = 'var(--border)';
        const Left = (c, t) => `inset ${t}px 0px 0px 0px ${c}`;
        const Right = (c, t) => `inset -${t}px 0px 0px 0px ${c}`;
        const Top = (c, t) => `inset 0px ${t}px 0px 0px ${c}`;
        const Bottom = (c, t) => `inset 0px -${t}px 0px 0px ${c}`;

        const selectedRows = R.uniq(R.pluck(0, selected_cell).sort());
        const selectedCols = R.uniq(R.pluck(1, selected_cell).sort());

        const showInsideLeftEdge = (
             (ci === R.head(selectedCols))
              && R.contains(ri, selectedRows)
        );
        const showInsideTopEdge = (
            (ri === R.head(selectedRows))
             && R.contains(ci, selectedCols)
        );
        const showOutsideTopEdge = (
            (ri === (R.last(selectedRows) + 1))
             && R.contains(ci, selectedCols)
        );
        const showOutsideLeftEdge = (
            (ci === (R.last(selectedCols) + 1))
             && R.contains(ri, selectedRows)
        );

        const showInsideRightEdge = (
            (ci === R.last(selectedCols))
             && R.contains(ri, selectedRows)
        );

        const showBottomEdge = (
            (ri === R.last(selectedRows) ||
             false // ri === (R.head(selectedRows) - 1)
         ) &&
             R.contains(ci, selectedCols)
        );

        const isRightmost = ci === R.last(vci);
        const isLeftmost = ci === R.head(vci);
        const isTopmost = ri === 0;
        const isBottommost = ri === (dataframe.length - 1);
        const isNeighborToExpanded = (
            collapsable &&
            R.contains(ri, expanded_rows) &&
            ci === vci[0]
        );
        const isAboveExpanded = (
            collapsable && R.contains(ri, expanded_rows)
        );
        const isBelowExpanded = (
            collapsable && R.contains(ri - 1, expanded_rows)
        );

        // rules are applied in the order that they are supplied
        const boxShadowRules = [

            showInsideLeftEdge || isNeighborToExpanded ? Left(Accent, 2) : null,
            showInsideTopEdge ? Top(Accent, 2) : null,
            showOutsideTopEdge && !isBelowExpanded ? Top(Accent, 1) : null,
            showOutsideLeftEdge ? Left(Accent, 1) : null,
            showBottomEdge ? Bottom(Accent, isBottommost || isAboveExpanded ? 2 : 1) : null,
            showInsideRightEdge ? Right(Accent, isRightmost ? 2 : 1) : null,

            Left(Border, 1),
            Top(Border, 1),

            isBottommost || isAboveExpanded ? Bottom(Border, 1) : null,
            isRightmost ? Right(Border, 1) : null

            // Right(Border, 1),
            // Bottom(Border, 1)

            // showLeftEdge || isNeighborToExpanded ?
            //     Left(Accent, isLeftmost ? 2 : 2) : Left(Border, 1),
            //
            // showRightEdge ? null : isRightmost ? Right(Border, 1) : null,
            //
            // // showRightEdge ? Right(Accent, isRightmost ? 2 : 1) :
            // //     isRightmost ? Right(Border, 1) : null,
            //
            // showTopEdge ? Top(Accent, isTopmost ? 2 : 1) : Top(Border, 1),
            //
            // showBottomEdge ? Bottom(Accent, isBottommost ? 2 : 1) :
            //     isBottommost ? Bottom(Border, 1) : null,

        ].filter(R.complement(R.not));
        const sortedBoxRules = R.sort(
            (a, b) => R.contains(Accent, a) ? -1 : 1,
            boxShadowRules
        );

        const style = {
            boxShadow: `${sortedBoxRules.join(', ')}`
        }

        return style;
    }

    borderSquares() {
        const {
            i: ci,
            idx: ri,
            columns,
            selected_cell,
            dataframe,
            collapsable,
            expanded_rows
        } = this.props;

        const vci = [];  // visible col indices
        columns.forEach((c, i) => {if(!c.hidden) vci.push(i)});

        const selectedRows = R.uniq(R.pluck(0, selected_cell).sort());
        const selectedCols = R.uniq(R.pluck(1, selected_cell).sort());

        const isRight = (
             ci === (R.last(selectedCols) + 1)
        );
        const isBelow = (
             ri === (R.last(selectedRows) + 1)
        );

        const className = (
            (isRight && isBelow) ? 'bottom-right' : ''
        );
        if (!className) return null
        console.info('*******', className);
        return (
            <div className={`selected-square selected-square-${className}`}/>
        );

    }


    render() {
        const {
            c,
            editable,
            i,
            idx,
            isSelected,
            isRight,
            isRightmost,
            isBottom,
            isBottommost,
            type,
            value,
            setProps,
            dataframe,
            is_focused,
            collapsable,
            expanded_rows,
            start_cell,
            selected_cell
        } = this.props;

        let innerCell;
        if (editable) {
            innerCell = <input
                id={`${c.name}-${idx}`}
                type="text"
                value={value}

                onClick={this.handleClick}
                onDoubleClick={this.handleDoubleClick}

                ref={el => this.textInput = el}

                onChange={e => {
                    if (isSelected) {
                        const newDataframe = R.set(R.lensPath([
                            idx, c.name
                        ]), e.target.value, dataframe);
                        setProps({
                            is_focused: true,
                            dataframe: newDataframe
                        });
                    }
                }}

                onPaste={e => {
                    if (!(isSelected && is_focused)) {
                        e.preventDefault();
                    }
                }}

                className={
                    (isSelected ? 'input-active ' : '') +
                    (is_focused && isSelected ? 'focused ' : 'unfocused ')
                }

            />
        } else {
            innerCell = value;
        }

        if (editable) {
            return (
                <td
                    style={this.borderStyle()}
                    className={(
                        (isSelected ? 'cell--active ' : '') +
                        (is_focused && isSelected ? 'focused ' : '') +
                        ((isSelected && selected_cell.length > 1 &&
                            !(start_cell[0] === idx && start_cell[1] === i)
                        ) ? 'cell--active--not-start' : '')
                    )}
                >

                    {innerCell}

                    {this.borderSquares()}

                </td>
            );
        } else {
            return (
                <td>
                    {value}
                </td>
            );
        }
    }
}
