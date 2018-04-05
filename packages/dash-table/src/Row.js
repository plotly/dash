import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import * as R from 'ramda';
import {keys, merge} from 'ramda';

import Cell from './Cell';

export default class Row extends Component {


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
            expanded_rows
        } = this.props;

        return (
            <tr>
                {!collapsable ? null : (
                    <td className='toggle-row'
                        onClick={e => {
                            if (R.contains(idx, expanded_rows)) {
                                setProps({
                                    expanded_rows:
                                    R.reject(R.equals(idx), expanded_rows)
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
                            '▼' : '►'
                        }
                    </td>
                )}

                {columns.map((c, i) => (
                    <Cell
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
                ))}
            </tr>
        );
    }
}

/*

                {!(collapsable && R.contains(idx, expanded_rows)) ? null :
                    <div>
                        <h1>
                            {'Summary'}
                        </h1>
                    </div>
                }

*/
