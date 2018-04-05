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
    }

    handleClick(e) {
        const {
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
            );
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
            is_focused
        } = this.props;

        console.warn('render');

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
                    className={(
                        (isSelected ? 'cell--active ' : '') +
                        (isRight ? 'cell--active-right ' : '') +
                        (isBottom ? 'cell--active-bottom ' : '') +
                        (isRightmost ? 'cell--right-last ' : '') +
                        (isBottommost ? 'cell--bottom-last ' : '') +
                        (is_focused && isSelected ? 'focused ' : '')
                    )}
                >

                    {innerCell}

                    {!isSelected ? null :
                        <div className="selected-square">

                        </div>
                    }

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
