import React, {Component} from 'react';
import PropTypes from 'prop-types';
import * as R from 'ramda';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import angleRight from '@fortawesome/fontawesome-free-solid/faAngleRight';
import angleDown from '@fortawesome/fontawesome-free-solid/faAngleDown';
import Cell from './Cell';
import computedStyles from './computedStyles';

const getColLength = c => (Array.isArray(c.name) ? c.name.length : 1);

export default class Row extends Component {
    render() {
        const {
            columns,
            dataframe,
            idx,
            editable,
            setProps,
            selected_cell,
            collapsable,
            expanded_rows,
        } = this.props;

        const collapsableCell = !collapsable ? null : (
            <td
                className={`toggle-row
                ${
                    R.contains(idx, expanded_rows) ? 'toggle-row--expanded' : ''
                }`}
                onClick={() => {
                    console.info(`Click ${idx}, ${expanded_rows}`);
                    if (R.contains(idx, expanded_rows)) {
                        setProps({
                            expanded_rows: R.without([idx], expanded_rows),
                        });
                    } else {
                        setProps({
                            expanded_rows: R.append(idx, expanded_rows),
                        });
                    }
                }}
            >
                {R.contains(idx, expanded_rows) ? (
                    <FontAwesomeIcon icon={angleDown} />
                ) : (
                    <FontAwesomeIcon icon={angleRight} />
                )}
            </td>
        );

        const cells = columns.map((c, i) => {
            if (c.hidden) {
                return null;
            }

            return (
                <Cell
                    key={`${c}-${i}`}
                    value={dataframe[idx][c.id]}
                    type={c.type}
                    editable={editable}
                    isSelected={R.contains([idx, i], selected_cell)}
                    idx={idx}
                    i={i}
                    c={c}
                    setProps={setProps}
                    {...this.props}
                />
            );
        });

        // TODO calculate in lifecycle function
        const headerDepth = Math.max.apply(Math, columns.map(getColLength));
        return (
            <tr
                style={computedStyles.scroll.row(this.props, idx + headerDepth)}
            >
                {collapsableCell}

                {cells}
            </tr>
        );
    }
}

Row.propTypes = {
    columns: PropTypes.any,
    dataframe: PropTypes.any,
    idx: PropTypes.any,
    editable: PropTypes.any,
    setProps: PropTypes.any,
    selected_cell: PropTypes.any,
    collapsable: PropTypes.any,
    expanded_rows: PropTypes.any,
    active_cell: PropTypes.any,
};
