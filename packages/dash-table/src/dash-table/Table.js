import React, { Component } from 'react';
import PropTypes from 'prop-types';

import RealTable from 'dash-table/components/Table';

import 'dash-table/style/component.less';
import Logger from 'core/Logger';

import genRandomId from './utils/generate';

function isFrontEnd(value) {
    return ['fe', true, false].indexOf(value) !== -1;
}

function isBackEnd(value) {
    return ['be', false].indexOf(value) !== -1;
}

export default class Table extends Component {
    constructor(props) {
        super(props);

        let id;
        this.getId = () => (id = id || genRandomId('table-'));
    }

    render() {
        const {
            filtering,
            sorting,
            pagination_mode
        } = this.props;

        const isValid = isFrontEnd(pagination_mode) ||
            (isBackEnd(filtering) && isBackEnd(sorting));

        if (!isValid) {
            Logger.error(`Invalid combination of filtering / sorting / pagination`, filtering, sorting, pagination_mode);
            return (<div>Invalid props combination</div>);
        }

        return this.props.id ? (<RealTable {...this.props} />) : (<RealTable {...this.props} id={this.getId()} />);
    }
}

export const defaultProps = {
    pagination_mode: 'fe',
    pagination_settings: {
        displayed_pages: 1,
        current_page: 0,
        page_size: 250
    },
    navigation: 'page',

    content_style: 'fit',
    css: [],
    filtering: false,
    filtering_settings: '',
    filtering_type: 'basic',
    filtering_types: ['basic'],
    sorting: false,
    sorting_type: 'single',
    sorting_settings: [],

    derived_viewport_data: [],
    derived_viewport_indices: [],
    derived_virtual_data: [],
    derived_virtual_indices: [],

    column_conditional_dropdowns: [],
    column_static_dropdown: [],

    data: [],
    columns: [],
    editable: false,
    active_cell: [],
    selected_cell: [[]],
    selected_rows: [],
    row_selectable: false,

    style_table: {},
    style_data_conditional: [],
    style_cell_conditional: [],
    style_header_conditional: []
};

export const propTypes = {
    active_cell: PropTypes.array,
    // .exact
    columns: PropTypes.arrayOf(PropTypes.shape({
        clearable: PropTypes.bool,
        deletable: PropTypes.oneOfType([
            PropTypes.bool,
            PropTypes.number
        ]),
        editable: PropTypes.bool,
        editable_name: PropTypes.oneOfType([
            PropTypes.bool,
            PropTypes.number
        ]),
        hidden: PropTypes.bool,
        id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        // .exact
        options: PropTypes.arrayOf(PropTypes.shape({
            label: PropTypes.oneOfType([
                PropTypes.number,
                PropTypes.string
            ]).isRequired,
            value: PropTypes.oneOfType([
                PropTypes.number,
                PropTypes.string
            ]).isRequired
        })),
        type: PropTypes.oneOf(['dropdown', 'numeric', 'text'])
    })),
    content_style: PropTypes.oneOf(['fit', 'grow']),
    // .exact
    css: PropTypes.arrayOf(PropTypes.shape({
        selector: PropTypes.string.isRequired,
        rule: PropTypes.string.isRequired
    })),

    data: PropTypes.arrayOf(PropTypes.object),
    data_previous: PropTypes.arrayOf(PropTypes.object),
    data_timestamp: PropTypes.number,

    editable: PropTypes.bool,
    end_cell: PropTypes.arrayOf(PropTypes.number),
    id: PropTypes.string,
    is_focused: PropTypes.bool,
    merge_duplicate_headers: PropTypes.bool,
    n_fixed_columns: PropTypes.number,
    n_fixed_rows: PropTypes.number,
    row_deletable: PropTypes.bool,
    row_selectable: PropTypes.oneOf(['single', 'multi', false]),
    selected_cell: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.number)),
    selected_rows: PropTypes.arrayOf(PropTypes.number),
    setProps: PropTypes.func,
    start_cell: PropTypes.arrayOf(PropTypes.number),
    style_as_list_view: PropTypes.bool,

    pagination_mode: PropTypes.oneOf(['fe', 'be', true, false]),
    // .exact
    pagination_settings: PropTypes.shape({
        displayed_pages: PropTypes.number.isRequired,
        current_page: PropTypes.number.isRequired,
        page_size: PropTypes.number.isRequired
    }),
    navigation: PropTypes.string,

    // .exact
    column_conditional_dropdowns: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.string.isRequired,
        // .exact
        dropdowns: PropTypes.arrayOf(PropTypes.shape({
            condition: PropTypes.string.isRequired,
            // .exact
            dropdown: PropTypes.arrayOf(PropTypes.shape({
                label: PropTypes.string.isRequired,
                value: PropTypes.oneOfType([
                    PropTypes.number,
                    PropTypes.string
                ]).isRequired
            })).isRequired
        })).isRequired
    })),
    // .exact
    column_static_dropdown: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.string.isRequired,
        // .exact
        dropdown: PropTypes.arrayOf(PropTypes.shape({
            label: PropTypes.string.isRequired,
            value: PropTypes.oneOfType([
                PropTypes.number,
                PropTypes.string
            ]).isRequired
        })).isRequired
    })),

    filtering: PropTypes.oneOf(['fe', 'be', true, false]),
    filtering_settings: PropTypes.string,
    filtering_type: PropTypes.oneOf(['basic']),
    filtering_types: PropTypes.arrayOf(PropTypes.oneOf([
        'basic'
    ])),

    sorting: PropTypes.oneOf(['fe', 'be', true, false]),
    sorting_type: PropTypes.oneOf(['single', 'multi']),
    sorting_settings: PropTypes.arrayOf(
        // .exact
        PropTypes.shape({
            columnId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
            direction: PropTypes.oneOf(['asc', 'desc']).isRequired
        })),
    sorting_treat_empty_string_as_none: PropTypes.bool,

    style_table: PropTypes.object,

    style_cell: PropTypes.object,
    style_data: PropTypes.object,
    style_filter: PropTypes.object,
    style_header: PropTypes.object,

    style_cell_conditional: PropTypes.arrayOf(PropTypes.shape({
        // .exact
        if: PropTypes.shape({
            column_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        })
    })),

    style_data_conditional: PropTypes.arrayOf(PropTypes.shape({
        // .exact
        if: PropTypes.shape({
            column_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
            row_index: PropTypes.oneOfType([
                PropTypes.number,
                PropTypes.oneOf(['odd', 'even'])
            ])
        })
    })),

    style_filter_conditional: PropTypes.arrayOf(PropTypes.shape({
        // .exact
        if: PropTypes.shape({
            column_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
        })
    })),

    style_header_conditional: PropTypes.arrayOf(PropTypes.shape({
        // .exact
        if: PropTypes.shape({
            column_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
            header_index: PropTypes.oneOfType([
                PropTypes.number,
                PropTypes.oneOf(['odd', 'even'])
            ])
        })
    })),

    derived_viewport_data: PropTypes.arrayOf(PropTypes.object),
    derived_viewport_indices: PropTypes.arrayOf(PropTypes.number),
    derived_virtual_data: PropTypes.arrayOf(PropTypes.object),
    derived_virtual_indices: PropTypes.arrayOf(PropTypes.number),

    dropdown_properties: PropTypes.any,
};

Table.defaultProps = defaultProps;
Table.propTypes = propTypes;