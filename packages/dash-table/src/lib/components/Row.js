import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import * as R from 'ramda';
import {keys, merge} from 'ramda';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import angleRight from '@fortawesome/fontawesome-free-solid/faAngleRight';
import angleDown from '@fortawesome/fontawesome-free-solid/faAngleDown';

import Cell from './Cell';
import computedStyles from './computedStyles';

export default class Row extends Component {
    shouldComponentUpdate(nextProps, nextState) {
        return true;

        const {
            selected_cell: prev_selected_cell,
            is_focused: prev_is_focused,
            start_cell: prev_start_cell,
            dataframe: prev_dataframe,
            expanded_rows: prev_expanded_rows
        } = this.props;

        const {
            idx,
            selected_cell,
            is_focused,
            start_cell,
            dataframe,
            expanded_rows
        } = nextProps;

        const shouldRender = (
            // row selection changes
            (!R.contains(idx, R.pluck(0, selected_cell)) &&
              R.contains(idx, R.pluck(0, prev_selected_cell))) ||

            ( R.contains(idx, R.pluck(0, selected_cell)) &&
             !R.contains(idx, R.pluck(0, prev_selected_cell))) ||

            // cell selection changes for the current row
            (R.contains(idx, R.pluck(0, selected_cell)) &&
             start_cell !== prev_start_cell) ||

            // row values change
            (dataframe[idx] !== prev_dataframe[idx]) ||

            // focus changes
            (R.contains(idx, R.pluck(0, selected_cell)) &&
             prev_is_focused !== is_focused) ||

            expanded_rows !== prev_expanded_rows
        );
        if (shouldRender) {
            console.info(`::Row ${idx} - ${shouldRender ? 'Render' : 'Skip'}`);
        }
        return shouldRender;
    }

    render()  {
        const {
            columns,
            dataframe,
            idx,
            c,
            types,
            editable,
            setProps,
            selected_cell,
            collapsable,
            expanded_rows,
            n_fixed_columns
        } = this.props;

        const collapsableCell = !collapsable ? null : (
            <td className={
                `toggle-row
                ${R.contains(idx, expanded_rows) ?
                    'toggle-row--expanded' : ''}`
            }
                onClick={e => {
                    console.info(`Click ${idx}, ${expanded_rows}`);
                    if (R.contains(idx, expanded_rows)) {
                        setProps({
                            expanded_rows:
                            R.without([idx], expanded_rows)
                        });
                    } else {
                        setProps({
                            expanded_rows:
                            R.append(idx, expanded_rows)
                        });
                    }

                }}

            >
                {R.contains(idx, expanded_rows) ?
                    <FontAwesomeIcon icon={angleDown}/>:
                    <FontAwesomeIcon icon={angleRight}/>
                }
            </td>
        );

        const cells = columns.map((c, i) => {
            if (c.hidden) return null;

            return (
            <Cell
                key={`${c}-${i}`}
                value={dataframe[idx][c.name]}
                type={c.type}
                editable={editable}

                isSelected={R.contains([idx, i], selected_cell)}

                isBottom={
                    false &&
                    selected_cell[0][0] === idx-1 &&
                    selected_cell[0][1] === i
                }
                isRight={
                    false &&
                    selected_cell[0][0] === idx &&
                    selected_cell[0][1] === i-1
                }
                isRightmost={
                    false &&
                    columns.length === (i + 1)
                }
                isBottommost={
                    false &&
                    dataframe.length === (idx + 1)
                }

                idx={idx}
                i={i}
                c={c}
                setProps={setProps}
                {...this.props}
            />

        )});

        return (
            <tr style={computedStyles.scroll.row(
                    this.props,
                    idx + (
                        R.has('rows', this.props.columns[0]) ?
                        this.props.columns[0].rows.length :
                        1
                    )
                )}>
                {collapsableCell}

                {cells}

            </tr>
        );
    }
}
