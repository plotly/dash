import React, {Component} from 'react';
import PropTypes from 'prop-types';
import * as R from 'ramda';

import ControlledTable from 'dash-table/components/ControlledTable';

import 'react-select/dist/react-select.css';
import './Table/Table.less';
import './Table/Dropdown.css';

import VirtualizationFactory from 'dash-table/virtualization/Factory';

import { memoizeOne } from 'core/memoizer';
import VirtualizationAdapter from 'dash-table/components/Table/VirtualizationAdapter';

export default class Table extends Component {
    constructor(props) {
        super(props);

        const setProps = memoizeOne(target => {
            return this.props.setProps || (newProps => target.setState(newProps));
        });

        const getVirtualizer = memoizeOne((target, virtualization) => {
            return VirtualizationFactory.getVirtualizer(target, virtualization);
        });

        const getAdapter = memoizeOne(target => new VirtualizationAdapter(target));

        Object.defineProperty(this, 'virtualizer', {
            get: () => getVirtualizer(getAdapter(this))
        });

        Object.defineProperty(this, 'setProps', {
            get: () => setProps(this)
        });
    }

    render() {
        this.virtualizer.refresh();

        if (!this.props.setProps) {
            const newProps = R.mergeAll([
                this.props,
                this.state,
                {
                    virtualizer: this.virtualizer,
                    setProps: this.setProps,
                },
            ]);
            return <ControlledTable {...newProps} />;
        }

        return (
            <ControlledTable
                {...R.merge(this.props, {
                    virtualizer: this.virtualizer,
                    setProps: newProps => {
                        if (R.has('dataframe', newProps)) {
                            const { dataframe } = this.props;

                            newProps.dataframe_timestamp = Date.now();
                            newProps.dataframe_previous = dataframe;
                        }

                        this.props.setProps(newProps);
                    },
                })}
            />
        );
    }
}

export const defaultProps = {
    virtualization: 'fe',
    virtualization_settings: {
        displayed_pages: 1,
        current_page: 0,
        page_size: 250
    },
    navigation: 'page',

    filtering: {
        type: 'fe',
        options: []
    },
    sorting: {
        type: 'fe',
        options: []
    },

    virtual_dataframe: [],
    virtual_dataframe_indices: [],

    changed_data: {},
    dataframe: [],
    columns: [],
    editable: false,
    active_cell: [],
    index_name: '',
    types: {},
    merged_styles: {},
    selected_cell: [[]],
    selected_rows: [],
    row_selectable: false,
    sort: [],
    table_style: [],
    base_styles: {
        numeric: {
            'text-align': 'right',
            'font-family': "'Droid Sans Mono', Courier, monospace",
        },

        string: {
            'text-align': 'left',
        },

        input: {
            padding: 0,
            margin: 0,
            width: '80px',
            border: 'none',
            'font-size': '1rem',
        },

        'input-active': {
            outline: '#7FDBFF auto 3px',
        },

        table: {},

        thead: {},

        th: {},

        td: {},
    }
};

export const propTypes = {
    active_cell: PropTypes.array,
    columns: PropTypes.arrayOf(PropTypes.object),

    dataframe: PropTypes.arrayOf(PropTypes.object),
    dataframe_previous: PropTypes.arrayOf(PropTypes.object),
    dataframe_timestamp: PropTypes.any,

    dropdown_properties: PropTypes.objectOf(
        PropTypes.arrayOf(PropTypes.shape({
            'options': PropTypes.shape({
                'label': PropTypes.string,
                'value': PropTypes.string,
                'required': PropTypes.bool
            }),
            'disabled': PropTypes.bool,
            // And the rest of the dropdown props...
        }))
    ),

    editable: PropTypes.bool,
    end_cell: PropTypes.arrayOf(PropTypes.number),
    id: PropTypes.string.isRequired,
    is_focused: PropTypes.bool,
    merge_duplicate_headers: PropTypes.bool,
    n_fixed_columns: PropTypes.number,
    n_fixed_rows: PropTypes.number,
    row_deletable: PropTypes.bool,
    row_selectable: PropTypes.oneOf(['single', 'multi']),
    selected_cell: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.number)),
    selected_rows: PropTypes.arrayOf(PropTypes.number),
    setProps: PropTypes.any,
    sort: PropTypes.array,
    sortable: PropTypes.bool,
    start_cell: PropTypes.arrayOf(PropTypes.number),
    style_as_list_view: PropTypes.bool,
    table_style: PropTypes.arrayOf(PropTypes.shape({
        selector: PropTypes.string,
        rule: PropTypes.string
    })),

    virtualization: PropTypes.string,
    virtualization_settings: PropTypes.shape({
        displayed_pages: PropTypes.number,
        current_page: PropTypes.number,
        page_size: PropTypes.number
    }),
    navigation: PropTypes.string,

    filtering: PropTypes.shape({
        type: PropTypes.string,
        options: PropTypes.arrayOf(
            PropTypes.shape({
                field: PropTypes.string,
                rule: PropTypes.any
            })
        )
    }),
    sorting: PropTypes.shape({
        type: PropTypes.string,
        options: PropTypes.arrayOf(
            PropTypes.shape({
                field: PropTypes.string,
                ascending: PropTypes.boolean
            })
        )
    }),

    virtual_dataframe: PropTypes.arrayOf(PropTypes.object),
    virtual_dataframe_indices: PropTypes.arrayOf(PropTypes.number),
};

Table.defaultProps = defaultProps;
Table.propTypes = propTypes;