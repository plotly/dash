import React, { Component } from 'react';
import PropTypes from 'prop-types';

import RealTable from 'dash-table/components/Table';

import 'dash-table/style/component.less';

export default class Table extends Component {
    render() {
        return (<RealTable {...this.props} />);
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

    filtering: false,
    filtering_settings: '',
    sorting: false,
    sorting_type: 'single',
    sorting_settings: [],
    sorting_treat_empty_string_as_none: false,

    virtual_dataframe: [],
    virtual_dataframe_indices: [],

    column_conditional_dropdowns: [],
    column_static_dropdown: [],

    column_conditional_styles: [],
    column_static_style: [],

    row_conditional_styles: [],
    row_static_style: {},

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
    table_style: [],
    base_styles: {
        numeric: {
            'text-align': 'right',
            'font-family': `'Droid Sans Mono', Courier, monospace`
        },

        string: {
            'text-align': 'left'
        },

        input: {
            padding: 0,
            margin: 0,
            width: '80px',
            border: 'none',
            'font-size': '1rem'
        },

        'input-active': {
            outline: '#7FDBFF auto 3px'
        },

        table: {},

        thead: {},

        th: {},

        td: {}
    }
};

export const propTypes = {
    active_cell: PropTypes.array,
    columns: PropTypes.arrayOf(PropTypes.object),

    dataframe: PropTypes.arrayOf(PropTypes.object),
    dataframe_previous: PropTypes.arrayOf(PropTypes.object),
    dataframe_timestamp: PropTypes.any,

    editable: PropTypes.bool,
    end_cell: PropTypes.arrayOf(PropTypes.number),
    id: PropTypes.string.isRequired,
    is_focused: PropTypes.bool,
    merge_duplicate_headers: PropTypes.bool,
    n_fixed_columns: PropTypes.number,
    n_fixed_rows: PropTypes.number,
    row_deletable: PropTypes.bool,
    row_selectable: PropTypes.oneOf(['single', 'multi', false]),
    selected_cell: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.number)),
    selected_rows: PropTypes.arrayOf(PropTypes.number),
    setProps: PropTypes.any,
    start_cell: PropTypes.arrayOf(PropTypes.number),
    style_as_list_view: PropTypes.bool,
    table_style: PropTypes.arrayOf(PropTypes.shape({
        selector: PropTypes.string,
        rule: PropTypes.string
    })),

    virtualization: PropTypes.oneOf(['fe', 'be', true, false]),
    virtualization_settings: PropTypes.shape({
        displayed_pages: PropTypes.number,
        current_page: PropTypes.number,
        page_size: PropTypes.number
    }),
    navigation: PropTypes.string,

    column_conditional_dropdowns: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.string,
        dropdowns: PropTypes.arrayOf(PropTypes.shape({
            condition: PropTypes.string,
            dropdown: PropTypes.arrayOf(PropTypes.shape({
                label: PropTypes.string,
                value: PropTypes.any
            }))
        }))
    })),
    column_static_dropdown: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.string,
        dropdown: PropTypes.arrayOf(PropTypes.shape({
            label: PropTypes.string,
            value: PropTypes.any
        }))
    })),

    column_conditional_style: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.string,
        styles: PropTypes.arrayOf(PropTypes.shape({
            condition: PropTypes.string,
            style: PropTypes.object
        }))
    })),
    column_static_style: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.string,
        style: PropTypes.object
    })),

    row_conditional_styles: PropTypes.arrayOf(PropTypes.shape({
        condition: PropTypes.string,
        style: PropTypes.object
    })),
    row_static_style: PropTypes.object,

    filtering: PropTypes.oneOf(['fe', 'be', true, false]),
    filtering_settings: PropTypes.string,

    sorting: PropTypes.oneOf(['fe', 'be', true, false]),
    sorting_type: PropTypes.oneOf(['single', 'multi']),
    sorting_settings: PropTypes.arrayOf(
        PropTypes.shape({
            columnId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
            direction: PropTypes.oneOf(['asc', 'desc'])
        })
    ),
    sorting_treat_empty_string_as_none: PropTypes.bool,

    virtual_dataframe: PropTypes.arrayOf(PropTypes.object),
    virtual_dataframe_indices: PropTypes.arrayOf(PropTypes.number),

    dropdown_properties: PropTypes.any,
};

Table.defaultProps = defaultProps;
Table.propTypes = propTypes;