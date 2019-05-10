import * as R from 'ramda';
import React, { Component } from 'react';
import PropTypes from 'prop-types';

import RealTable from 'dash-table/components/Table';

import Logger from 'core/Logger';

import genRandomId from 'dash-table/utils/generate';
import isValidProps from './validate';
import sanitizeProps from './sanitize';

export default class DataTable extends Component {
    constructor(props) {
        super(props);

        let id;
        this.getId = () => (id = id || genRandomId('table-'));
    }

    render() {
        if (!isValidProps(this.props)) {
            return (<div>Invalid props combination</div>);
        }

        const sanitizedProps = sanitizeProps(this.props);
        return this.props.id ?
            (<RealTable {...sanitizedProps} />) :
            (<RealTable {...sanitizedProps} id={this.getId()} />);
    }
}

export const defaultProps = {
    pagination_mode: 'fe',
    pagination_settings: {
        current_page: 0,
        page_size: 250
    },
    navigation: 'page',

    content_style: 'grow',
    css: [],
    filter: '',
    filtering: false,
    filtering_type: 'basic',
    filtering_types: ['basic'],
    sorting: false,
    sorting_type: 'single',
    sort_by: [],
    style_as_list_view: false,

    derived_viewport_data: [],
    derived_viewport_indices: [],
    derived_viewport_row_ids: [],
    derived_viewport_selected_rows: [],
    derived_viewport_selected_row_ids: [],
    derived_virtual_data: [],
    derived_virtual_indices: [],
    derived_virtual_row_ids: [],
    derived_virtual_selected_rows: [],
    derived_virtual_selected_row_ids: [],

    column_conditional_dropdowns: [],
    column_static_dropdown: [],

    column_static_tooltip: {},
    column_conditional_tooltips: [],
    tooltip_delay: 350,
    tooltip_duration: 2000,

    data: [],
    columns: [],
    editable: false,
    selected_cells: [],
    selected_rows: [],
    selected_row_ids: [],
    row_selectable: false,

    style_table: {},
    style_cell_conditional: [],
    style_data_conditional: [],
    style_filter_conditional: [],
    style_header_conditional: [],
    virtualization: false
};

export const propTypes = {
    /**
     * The row and column indices and IDs of the currently active cell.
     */
    active_cell: PropTypes.exact({
        row: PropTypes.number,
        column: PropTypes.number,
        row_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        column_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    }),

    /**
     * Columns describes various aspects about each individual column.
     * `name` and `id` are the only required parameters.
     */
    columns: PropTypes.arrayOf(PropTypes.shape({

        /**
         * If the column is rendered as dropdowns, then the
         * `clearable` property determines whether or not
         * the dropdown value can be cleared or not.
         *
         * NOTE - The name of this property may change in the future,
         * subscribe to [https://github.com/plotly/dash-table/issues/168](https://github.com/plotly/dash-table/issues/168)
         * for more information.
         */
        clearable: PropTypes.bool,

        /**
         * If True, the user can delete the column by clicking on a little `x`
         * button on the column.
         * If there are merged, multi-header columns then you can choose
         * which column header row to display the "x" in by
         * supplying a column row index.
         * For example, `0` will display the "x" on the first row,
         * `1` on the second row.
         * If the "x" appears on a merged column, then clicking on that button
         * will delete *all* of the merged columns associated with it.
         */
        deletable: PropTypes.oneOfType([
            PropTypes.bool,
            PropTypes.number
        ]),

        /**
         * There are two `editable` flags in the table.
         * This is the  column-level editable flag and there is
         * also the table-level `editable` flag.
         *
         * These flags determine whether the contents of the table
         * are editable or not.
         *
         * If the column-level `editable` flag is set it overrides
         * the table-level `editable` flag for that column.
         */
        editable: PropTypes.bool,

        /**
         * If True, then the name of this column is editable.
         * If there are multiple column headers (if `name` is a list of strings),
         * then `editable_name` can refer to _which_ column header should be
         * editable by setting it to the column header index.
         * Also, updating the name in a merged column header cell will
         * update the name of each column.
         */
        editable_name: PropTypes.oneOfType([
            PropTypes.bool,
            PropTypes.number
        ]),

        /**
         * The formatting applied to the column's data.
         *
         * This prop is derived from the [d3-format](https://github.com/d3/d3-format) library specification. Apart from
         * being structured slightly differently (under a single prop), the usage
         * is the same.
         *
         * 'locale': represents localization specific formatting information
         *   When left unspecified, will use the default value provided by d3-format.
         *
         *   'symbol': (default: ['$', '']) a list of two strings representing the
         *   prefix and suffix symbols. Typically used for currency, and implemented using d3's
         *   currency format, but you can use this for other symbols such as measurement units.
         *   'decimal': (default: '.') the string used for the decimal separator
         *   'group': (default: ',') the string used for the groups separator
         *   'grouping': (default: [3]) a list of integers representing the grouping pattern
         *   'numerals': a list of ten strings used as replacements for numbers 0-9
         *   'percent': (default: '%') the string used for the percentage symbol
         *   'separate_4digits': (default: True) separate integers with 4-digits or less
         *
         * 'nully': a value that will be used in place of the nully value during formatting
         *   If the value type matches the column type, it will be formatted normally
         * 'prefix': a number representing the SI unit to use during formatting
         *   See `dash_table.Format.Prefix` enumeration for the list of valid values
         * 'specifier': (default: '') represents the rules to apply when formatting the number
         *
         * dash_table.FormatTemplate contains helper functions to rapidly use certain
         * typical number formats.
         */
        format: PropTypes.shape({
            locale: PropTypes.shape({
                symbol: PropTypes.arrayOf(PropTypes.string),
                decimal: PropTypes.string,
                group: PropTypes.string,
                grouping: PropTypes.arrayOf(PropTypes.number),
                numerals: PropTypes.arrayOf(PropTypes.string),
                percent: PropTypes.string,
                separate_4digits: PropTypes.bool
            }),
            nully: PropTypes.any,
            prefix: PropTypes.number,
            specifier: PropTypes.string
        }),

        /**
         * If True, then the column and its data is hidden.
         * This can be useful if you want to transport extra
         * meta data (like a data index) to and from callbacks
         * but you don't necessarily want to display that data.
         */
        hidden: PropTypes.bool,

        /**
         * The `id` of the column.
         * The column `id` is used to match cells in data
         * with particular columns.
         * The `id` is not visible in the table.
         */
        id: PropTypes.string.isRequired,
        /**
         * The `name` of the column,
         * as it appears in the column header.
         * If `name` is a list of strings, then the columns
         * will render with multiple headers rows.
         */
        name: PropTypes.oneOfType([
            PropTypes.string,
            PropTypes.arrayOf(PropTypes.string)
        ]).isRequired,

        /**
         * The `presentation` to use to display the value.
         * Defaults to 'input' for ['numeric', 'text', 'any'].
         */
        presentation: PropTypes.oneOf(['input', 'dropdown']),

        /**
         * The `on_change` behavior of the column for user-initiated modifications.
         * 'action' (default 'coerce'):
         *  none: do not validate data
         *  coerce: check if the data corresponds to the destination type and
         *  attempts to coerce it into the destination type if not
         *  validate: check if the data corresponds to the destination type (no coercion)
         *
         * 'failure' (default 'reject'): what to do with the value if the action fails
         *  accept: use the invalid value
         *  default: replace the provided value with `validation.default`
         *  reject: do not modify the existing value
         */
        on_change: PropTypes.shape({
            action: PropTypes.oneOf([
                'coerce',
                'none',
                'validate'
            ]),
            failure: PropTypes.oneOf([
                'accept',
                'default',
                'reject'
            ])
        }),

        /**
         * The `validation` options.
         * 'allow_null': Allow the use of nully values (undefined, null, NaN) (default: false)
         * 'default': The default value to apply with on_change.failure = 'default' (default: null)
         * 'allow_YY': `datetime` columns only, allow 2-digit years (default: false).
         *   If true, we interpret years as ranging from now-70 to now+29 - in 2019
         *   this is 1949 to 2048 but in 2020 it will be different. If used with
         *   `action: 'coerce'`, will convert user input to a 4-digit year.
         */
        validation: PropTypes.shape({
            allow_null: PropTypes.bool,
            default: PropTypes.any,
            allow_YY: PropTypes.bool
        }),

        /**
         * DEPRECATED
         * Please use `column_static_dropdown` instead.
         * NOTE - Dropdown behavior will likely change in the future,
         * subscribe to [https://github.com/plotly/dash-table/issues/168](https://github.com/plotly/dash-table/issues/168)
         * for more information.
         */
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

        /**
         * The data-type of the column's data.
         * 'numeric': represents both floats and ints
         * 'text': represents a string
         * 'datetime': a string representing a date or date-time, in the form:
         *   'YYYY-MM-DD HH:MM:SS.ssssss' or some truncation thereof. Years must
         *   have 4 digits, unless you use `validation.allow_YY: true`. Also
         *   accepts 'T' or 't' between date and time, and allows timezone info
         *   at the end. To convert these strings to Python `datetime` objects,
         *   use `dateutil.parser.isoparse`. In R use `parse_iso_8601` from the
         *   `parsedate` library.
         *   WARNING: these parsers do not work with 2-digit years, if you use
         *   `validation.allow_YY: true` and do not coerce to 4-digit years.
         *   And parsers that do work with 2-digit years may make a different
         *   guess about the century than we make on the front end.
         * 'any': represents any type of data
         *
         * Defaults to 'any' if undefined.
         *
         * NOTE: This feature has not been fully implemented.
         * In the future, it's data types will impact things like
         * text formatting options in the cell (e.g. display 2 decimals
         * for a number), filtering options and behavior, and editing
         * behavior.
         * Stay tuned by following [https://github.com/plotly/dash-table/issues/166](https://github.com/plotly/dash-table/issues/166)
         */
        type: PropTypes.oneOf(['any', 'numeric', 'text', 'datetime'])
    })),

    /**
     * The localization specific formatting information applied to all columns in the table.
     *
     * This prop is derived from the [d3.formatLocale](https://github.com/d3/d3-format#formatLocale) data structure specification.
     *
     * When left unspecified, each individual nested prop will default to a pre-determined value.
     *
     *   'symbol': (default: ['$', '']) a list of two strings representing the
     *   prefix and suffix symbols. Typically used for currency, and implemented using d3's
     *   currency format, but you can use this for other symbols such as measurement units.
     *   'decimal': (default: '.') the string used for the decimal separator
     *   'group': (default: ',') the string used for the groups separator
     *   'grouping': (default: [3]) a list of integers representing the grouping pattern
     *   'numerals': a list of ten strings used as replacements for numbers 0-9
     *   'percent': (default: '%') the string used for the percentage symbol
     *   'separate_4digits': (default: True) separate integers with 4-digits or less
     */
    locale_format: PropTypes.shape({
        symbol: PropTypes.arrayOf(PropTypes.string),
        decimal: PropTypes.string,
        group: PropTypes.string,
        grouping: PropTypes.arrayOf(PropTypes.number),
        numerals: PropTypes.arrayOf(PropTypes.string),
        percent: PropTypes.string,
        separate_4digits: PropTypes.bool
    }),

    /**
     * `content_style` toggles between a set of CSS styles for
     * two common behaviors:
     * - `fit`: The table container's width be equal to the width of its content.
     * - `grow`: The table container's width will grow to be the size of the container.
     *
     * NOTE - This property will likely change in the future,
     * subscribe to [https://github.com/plotly/dash-table/issues/176](https://github.com/plotly/dash-table/issues/176)
     * for more details.
     */
    content_style: PropTypes.oneOf(['fit', 'grow']),
    /**
     * The `css` property is a way to embed CSS selectors and rules
     * onto the page.
     * We recommend starting with the `style_*` properties
     * before using this `css` property.
     *
     * Example:
     * [
     *     {"selector": ".dash-spreadsheet", "rule": 'font-family: "monospace"'}
     * ]
     *
     */
    css: PropTypes.arrayOf(PropTypes.shape({
        selector: PropTypes.string.isRequired,
        rule: PropTypes.string.isRequired
    })),

    /**
     * The contents of the table.
     * The keys of each item in data should match the column IDs.
     * Each item can also have an 'id' key, whose value is its row ID. If there
     * is a column with ID='id' this will display the row ID, otherwise it is
     * just used to reference the row for selections, filtering, etc.
     *
     * Example:
     *
     * [
     *      {'column-1': 4.5, 'column-2': 'montreal', 'column-3': 'canada'},
     *      {'column-1': 8, 'column-2': 'boston', 'column-3': 'america'}
     * ]
     *
     */
    data: PropTypes.arrayOf(PropTypes.object),

    /**
     * The previous state of `data`. `data_previous`
     * has the same structure as `data` and it will be updated
     * whenever `data` changes, either through a callback or
     * by editing the table.
     * This is a read-only property: setting this property will not
     * have any impact on the table.
     */
    data_previous: PropTypes.arrayOf(PropTypes.object),

    /**
     * The unix timestamp when the data was last edited.
     * Use this property with other timestamp properties
     * (such as `n_clicks_timestamp` in `dash_html_components`)
     * to determine which property has changed within a callback.
     */
    data_timestamp: PropTypes.number,

    /**
     * If True, then the data in all of the cells is editable.
     * When `editable` is True, particular columns can be made
     * uneditable by setting `editable` to `False` inside the `columns`
     * property.
     *
     * If False, then the data in all of the cells is uneditable.
     * When `editable` is False, particular columns can be made
     * editable by setting `editable` to `True` inside the `columns`
     * property.
     */
    editable: PropTypes.bool,

    /**
     * When selecting multiple cells
     * (via clicking on a cell and then shift-clicking on another cell),
     * `end_cell` represents the row / column coordinates and IDs of the cell
     * in one of the corners of the region.
     * `start_cell` represents the coordinates of the other corner.
     */
    end_cell: PropTypes.exact({
        row: PropTypes.number,
        column: PropTypes.number,
        row_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        column_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    }),

    /**
     * The ID of the table.
     */
    id: PropTypes.string,

    /**
     * If True, then the `active_cell` is in a focused state.
     */
    is_focused: PropTypes.bool,

    /**
     * If True, then column headers that have neighbors with duplicate names
     * will be merged into a single cell.
     * This will be applied for single column headers and multi-column
     * headers.
     */
    merge_duplicate_headers: PropTypes.bool,

    /**
     * `n_fixed_columns` will "fix" the set of columns so that
     * they remain visible when scrolling horizontally across
     * the unfixed columns. `n_fixed_columns` fixes columns
     * from left-to-right, so `n_fixed_columns=3` will fix
     * the first 3 columns.
     *
     * Note that fixing columns introduces some changes to the
     * underlying markup of the table and may impact the
     * way that your columns are rendered or sized.
     * View the documentation examples to learn more.
     */
    n_fixed_columns: PropTypes.number,

    /**
     * `n_fixed_rows` will "fix" the set of rows so that
     * they remain visible when scrolling vertically down
     * the table. `n_fixed_rows` fixes rows
     * from top-to-bottom, starting from the headers,
     * so `n_fixed_rows=1` will fix the header row,
     * `n_fixed_rows=2` will fix the header row and the first row,
     * or the first two header rows (if there are multiple headers).
     *
     * Note that fixing rows introduces some changes to the
     * underlying markup of the table and may impact the
     * way that your columns are rendered or sized.
     * View the documentation examples to learn more.
     */
    n_fixed_rows: PropTypes.number,

    /**
     * If True, then a `x` will appear next to each `row`
     * and the user can delete the row.
     */
    row_deletable: PropTypes.bool,

    /**
     * If `single`, then the user can select a single row
     * via a radio button that will appear next to each row.
     * If `multi`, then the user can select multiple rows
     * via a checkbox that will appear next to each row.
     * If `False`, then the user will not be able to select rows
     * and no additional UI elements will appear.
     *
     * When a row is selected, its index will be contained
     * in `selected_rows`.
     */
    row_selectable: PropTypes.oneOf(['single', 'multi', false]),

    /**
     * `selected_cells` represents the set of cells that are selected,
     * as an array of objects, each item similar to `active_cell`.
     * Multiple cells can be selected by holding down shift and
     * clicking on a different cell or holding down shift and navigating
     * with the arrow keys.
     */
    selected_cells: PropTypes.arrayOf(PropTypes.exact({
        row: PropTypes.number,
        column: PropTypes.number,
        row_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        column_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    })),

    /**
     * `selected_rows` contains the indices of rows that
     * are selected via the UI elements that appear when
     * `row_selectable` is `'single'` or `'multi'`.
     */
    selected_rows: PropTypes.arrayOf(PropTypes.number),

    /**
     * `selected_row_ids` contains the ids of rows that
     * are selected via the UI elements that appear when
     * `row_selectable` is `'single'` or `'multi'`.
     */
    selected_row_ids: PropTypes.arrayOf(
        PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    ),

    setProps: PropTypes.func,

    /**
     * When selecting multiple cells
     * (via clicking on a cell and then shift-clicking on another cell),
     * `start_cell` represents the [row, column] coordinates of the cell
     * in one of the corners of the region.
     * `end_cell` represents the coordinates of the other corner.
     */
    start_cell: PropTypes.exact({
        row: PropTypes.number,
        column: PropTypes.number,
        row_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        column_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    }),

    /**
     * If True, then the table will be styled like a list view
     * and not have borders between the columns.
     */
    style_as_list_view: PropTypes.bool,

    /**
     * "pagination" refers to a mode of the table where
     * not all of the rows are displayed at once: only a subset
     * are displayed (a "page") and the next subset of rows
     * can viewed by clicking "Next" or "Previous" buttons
     * at the bottom of the page.
     *
     * Pagination is used to improve performance: instead of
     * rendering all of the rows at once (which can be expensive),
     * we only display a subset of them.
     *
     * With pagination, we can either page through data that exists
     * in the table (e.g. page through `10,000` rows in `data` `100` rows at a time)
     * or we can update the data on-the-fly with callbacks
     * when the user clicks on the "Previous" or "Next" buttons.
     * These modes can be toggled with this `pagination_mode` parameter:
     * - `'fe'` refers to "front-end" paging: passing large data up-front
     * - `'be'` refers to "back-end" paging: updating the data on the fly via callbacks
     * - `False` will disable paging, attempting to render all of the data at once
     * - `True` is the same as `fe`
     *
     * NOTE: The `fe` and `be` names may change in the future.
     * Tune in to [https://github.com/plotly/dash-table/issues/167](https://github.com/plotly/dash-table/issues/167) for more.
     */
    pagination_mode: PropTypes.oneOf(['fe', 'be', true, false]),

    /**
     * `pagination_settings` controls the pagination settings
     * _and_ represents the current state of the pagination UI.
     * - `page_size` represents the number of rows that will be
     * displayed on a particular page.
     * - `current_page` represents which page the user is on.
     * Use this property to index through data in your callbacks with
     * backend paging.
     */
    pagination_settings: PropTypes.shape({
        current_page: PropTypes.number.isRequired,
        page_size: PropTypes.number.isRequired
    }),

    /**
     * DEPRECATED
     */
    navigation: PropTypes.string,

    /**
     * `column_conditional_dropdowns` specifies the available options
     * for dropdowns in various columns and cells.
     * This property allows you to specify different dropdowns
     * depending on certain conditions. For example, you may
     * render different "city" dropdowns in a row depending on the
     * current value in the "state" column.
     *
     * NOTE: The naming and the behavior of this option may change
     * in the future.
     * Tune in to [https://github.com/plotly/dash-table/issues/168](https://github.com/plotly/dash-table/issues/168)
     */
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
    /**
     * `column_static_dropdown` represents the available dropdown
     * options for different columns.
     * The `id` property refers to the column ID.
     * The `dropdown` property refers to the `options` of the
     * dropdown.
     *
     * NOTE: The naming and the behavior of this option may change
     * in the future.
     * Tune in to [https://github.com/plotly/dash-table/issues/168](https://github.com/plotly/dash-table/issues/168)
     */
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

    /**
     * `column_static_tooltip` represents the tooltip shown
     * for different columns.
     * The `property` name refers to the column ID.
     * The `type` refers to the type of tooltip syntax used
     * for the tooltip generation. Can either be `markdown`
     * or `text`. Defaults to `text`.
     * The `value` refers to the syntax-based content of
     * the tooltip. This value is required.
     * The `delay` represents the delay in milliseconds before
     * the tooltip is shown when hovering a cell. This overrides
     * the table's `tooltip_delay` property. If set to `null`,
     * the tooltip will be shown immediately.
     * The `duration` represents the duration in milliseconds
     * during which the tooltip is shown when hovering a cell.
     * This overrides the table's `tooltip_duration` property.
     * If set to `null`, the tooltip will not disappear.
     *
     * Alternatively, the value of the property can also be
     * a plain string. The `text` syntax will be used in
     * that case.
     */
    column_static_tooltip: PropTypes.objectOf(
        PropTypes.oneOfType([
            PropTypes.shape({
                delay: PropTypes.number,
                duration: PropTypes.number,
                type: PropTypes.oneOf([
                    'text',
                    'markdown'
                ]),
                value: PropTypes.string.isRequired
            }),
            PropTypes.string
        ])
    ),

    /**
     * `column_conditional_tooltips` represents the tooltip shown
     * for different columns and cells.
     *
     * This property allows you to specify different tooltips for
     * depending on certain conditions. For example, you may have
     * different tooltips in the same column based on the value
     * of a certain data property.
     *
     * Priority is from first to last defined conditional tooltip
     * in the list. Higher priority (more specific) conditional
     * tooltips should be put at the beginning of the list.
     *
     * The `if` refers to the condition that needs to be fulfilled
     * in order for the associated tooltip configuration to be
     * used. If multiple conditions are defined, all conditions
     * must be met for the tooltip to be used by a cell.
     *
     * The `if` nested property `column_id` refers to the column
     * ID that must be matched.
     * The `if` nested property `row_index` refers to the index
     * of the row in the source `data`.
     * The `if` nested property `filter` refers to the query that
     * must evaluate to True.
     *
     * The `type` refers to the type of tooltip syntax used
     * for the tooltip generation. Can either be `markdown`
     * or `text`. Defaults to `text`.
     * The `value` refers to the syntax-based content of
     * the tooltip. This value is required.
     * The `delay` represents the delay in milliseconds before
     * the tooltip is shown when hovering a cell. This overrides
     * the table's `tooltip_delay` property. If set to `null`,
     * the tooltip will be shown immediately.
     * The `duration` represents the duration in milliseconds
     * during which the tooltip is shown when hovering a cell.
     * This overrides the table's `tooltip_duration` property.
     * If set to `null`, the tooltip will not disappear.
     */
    column_conditional_tooltips: PropTypes.arrayOf(PropTypes.shape({
        if: PropTypes.shape({
            filter: PropTypes.string,
            row_index: PropTypes.oneOfType([
                PropTypes.number,
                PropTypes.oneOf([
                    'odd',
                    'even'
                ])
            ]),
            column_id: PropTypes.string
        }).isRequired,
        delay: PropTypes.number,
        duration: PropTypes.number,
        type: PropTypes.oneOf([
            'text',
            'markdown'
        ]),
        value: PropTypes.string.isRequired
    })),

    /**
     * `tooltips` represents the tooltip shown
     * for different columns and cells.
     * The `property` name refers to the column ID. Each property
     * contains a list of tooltips mapped to the source `data`
     * row index.
     *
     * The `type` refers to the type of tooltip syntax used
     * for the tooltip generation. Can either be `markdown`
     * or `text`. Defaults to `text`.
     * The `value` refers to the syntax-based content of
     * the tooltip. This value is required.
     * The `delay` represents the delay in milliseconds before
     * the tooltip is shown when hovering a cell. This overrides
     * the table's `tooltip_delay` property. If set to `null`,
     * the tooltip will be shown immediately.
     * The `duration` represents the duration in milliseconds
     * during which the tooltip is shown when hovering a cell.
     * This overrides the table's `tooltip_duration` property.
     * If set to `null`, the tooltip will not disappear.
     *
     * Alternatively, the value of the property can also be
     * a plain string. The `text` syntax will be used in
     * that case.
     */
    tooltips: PropTypes.objectOf(PropTypes.arrayOf(
        PropTypes.oneOfType([
            PropTypes.string,
            PropTypes.shape({
                delay: PropTypes.number,
                duration: PropTypes.number,
                type: PropTypes.oneOf([
                    'text',
                    'markdown'
                ]),
                value: PropTypes.string.isRequired
            })
        ]))
    ),

    /**
     * `tooltip_delay` represents the table-wide delay in milliseconds before
     * the tooltip is shown when hovering a cell. If set to `null`, the tooltip
     * will be shown immediately.
     *
     * Defaults to 350.
     */
    tooltip_delay: PropTypes.number,

    /**
     * `tooltip_duration` represents the table-wide duration in milliseconds
     * during which the tooltip will be displayed when hovering a cell. If
     * set to `null`, the tooltip will not disappear.
     *
     * Defaults to 2000.
     */
    tooltip_duration: PropTypes.number,

    /**
     * If `filtering` is enabled, then the current filtering
     * string is represented in this `filter`
     * property.
     * NOTE: The shape and structure of this property will
     * likely change in the future.
     * Stay tuned in [https://github.com/plotly/dash-table/issues/169](https://github.com/plotly/dash-table/issues/169)
     */
    filter: PropTypes.string,

    /**
     * The `filtering` property controls the behavior of the `filtering` UI.
     * If `False`, then the filtering UI is not displayed
     * If `fe` or True, then the filtering UI is displayed and the filtering
     * happens in the "front-end". That is, it is performed on the data
     * that exists in the `data` property.
     * If `be`, then the filtering UI is displayed but it is the
     * responsibility of the developer to program the filtering
     * through a callback (where `filter` would be the input
     * and `data` would be the output).
     *
     * NOTE - Several aspects of filtering may change in the future,
     * including the naming of this property.
     * Tune in to [https://github.com/plotly/dash-table/issues/167](https://github.com/plotly/dash-table/issues/167)
     */
    filtering: PropTypes.oneOf(['fe', 'be', true, false]),

    /**
     * UNSTABLE
     * In the future, there may be several modes of the
     * filtering UI like `basic`, `advanced`, etc.
     * Currently, we only `basic`.
     * NOTE - This will likely change in the future,
     * subscribe to changes here:
     * [https://github.com/plotly/dash-table/issues/169](https://github.com/plotly/dash-table/issues/169)
     */
    filtering_type: PropTypes.oneOf(['basic']),

    /**
     * UNSTABLE
     * In the future, there may be several modes of the
     * filtering UI like `basic`, `advanced`, etc
     * NOTE - This will likely change in the future,
     * subscribe to changes here:
     * [https://github.com/plotly/dash-table/issues/169](https://github.com/plotly/dash-table/issues/169)
     */
    filtering_types: PropTypes.arrayOf(PropTypes.oneOf([
        'basic'
    ])),

    /**
     * The `sorting` property enables data to be
     * sorted on a per-column basis.
     * Enabling `sorting` will display a UI element
     * on each of the columns (up and down arrows).
     *
     * Sorting can be performed in the "front-end"
     * with the `fe` (or True) setting or via a callback in your
     * python "back-end" with the `be` setting.
     * Clicking on the sort arrows will update the
     * `sort_by` property.
     */
    sorting: PropTypes.oneOf(['fe', 'be', true, false]),

    /**
     * Sorting can be performed across multiple columns
     * (e.g. sort by country, sort within each country,
     *  sort by year) or by a single column.
     *
     * NOTE - With multi-column sort, it's currently
     * not possible to determine the order in which
     * the columns were sorted through the UI.
     * See [https://github.com/plotly/dash-table/issues/170](https://github.com/plotly/dash-table/issues/170)
     */
    sorting_type: PropTypes.oneOf(['single', 'multi']),

    /**
     * `sort_by` describes the current state
     * of the sorting UI.
     * That is, if the user clicked on the sort arrow
     * of a column, then this property will be updated
     * with the column ID and the direction
     * (`asc` or `desc`) of the sort.
     * For multi-column sorting, this will be a list of
     * sorting parameters, in the order in which they were
     * clicked.
     */
    sort_by: PropTypes.arrayOf(
        // .exact
        PropTypes.shape({
            column_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
            direction: PropTypes.oneOf(['asc', 'desc']).isRequired
        })),

    /**
     * If False, then empty strings (`''`) are considered
     * valid values (they will appear first when sorting ascending).
     * If True, empty strings will be ignored, causing these cells to always
     * appear last.
     */
    sorting_treat_empty_string_as_none: PropTypes.bool,

    /**
     * CSS styles to be applied to the outer `table` container.
     *
     * This is commonly used for setting properties like the
     * width or the height of the table.
     */
    style_table: PropTypes.object,

    /**
     * CSS styles to be applied to each individual cell of the table.
     *
     * This includes the header cells, the `data` cells, and the filter
     * cells.
     */
    style_cell: PropTypes.object,

    /**
     * CSS styles to be applied to each individual data cell.
     *
     * That is, unlike `style_cell`, it excludes the header and filter cells.
     */
    style_data: PropTypes.object,

    /**
     * CSS styles to be applied to the filter cells.
     *
     * Note that this may change in the future as we build out a
     * more complex filtering UI.
     */
    style_filter: PropTypes.object,

    /**
     * CSS styles to be applied to each individual header cell.
     *
     * That is, unlike `style_cell`, it excludes the `data` and filter cells.
     */
    style_header: PropTypes.object,

    /**
     * Conditional CSS styles for the cells.
     *
     * This can be used to apply styles to cells on a per-column basis.
     */
    style_cell_conditional: PropTypes.arrayOf(PropTypes.shape({
        // .exact
        if: PropTypes.shape({
            column_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
            column_type: PropTypes.oneOf(['any', 'numeric', 'text', 'datetime'])
        })
    })),

    /**
     * Conditional CSS styles for the data cells.
     *
     * This can be used to apply styles to data cells on a per-column basis.
     */
    style_data_conditional: PropTypes.arrayOf(PropTypes.shape({
        // .exact
        if: PropTypes.shape({
            column_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
            column_type: PropTypes.oneOf(['any', 'numeric', 'text', 'datetime']),
            filter: PropTypes.string,
            row_index: PropTypes.oneOfType([
                PropTypes.number,
                PropTypes.oneOf(['odd', 'even'])
            ])
        })
    })),

    /**
     * Conditional CSS styles for the filter cells.
     *
     * This can be used to apply styles to filter cells on a per-column basis.
     */
    style_filter_conditional: PropTypes.arrayOf(PropTypes.shape({
        // .exact
        if: PropTypes.shape({
            column_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
            column_type: PropTypes.oneOf(['any', 'numeric', 'text', 'datetime'])
        })
    })),

    /**
     * Conditional CSS styles for the header cells.
     *
     * This can be used to apply styles to header cells on a per-column basis.
     */
    style_header_conditional: PropTypes.arrayOf(PropTypes.shape({
        // .exact
        if: PropTypes.shape({
            column_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
            column_type: PropTypes.oneOf(['any', 'numeric', 'text', 'datetime']),
            header_index: PropTypes.oneOfType([
                PropTypes.number,
                PropTypes.oneOf(['odd', 'even'])
            ])
        })
    })),

    /**
     * This property tells the table to use virtualization when rendering.
     *
     * Assumptions are that:
     * - the width of the columns is fixed
     * - the height of the rows is always the same
     * - runtime styling changes will not affect width and height vs. first rendering
     */
    virtualization: PropTypes.bool,

    /**
     * This property represents the current structure of
     * `filter` as a tree structure. Each node of the
     * query structure have:
     * - type (string; required)
     *   - 'open-block'
     *   - 'logical-operator'
     *   - 'relational-operator'
     *   - 'unary-operator'
     *   - 'expression'
     * - subType (string; optional)
     *   - 'open-block': '()'
     *   - 'logical-operator': '&&', '||'
     *   - 'relational-operator': '=', '>=', '>', '<=', '<', '!=', 'contains'
     *   - 'unary-operator': '!', 'is bool', 'is even', 'is nil', 'is num', 'is object', 'is odd', 'is prime', 'is str'
     *   - 'expression': 'value', 'field'
     * - value (any)
     *   - 'expression, value': passed value
     *   - 'expression, field': the field/prop name
     *
     * - block (nested query structure; optional)
     * - left (nested query structure; optional)
     * - right (nested query structure; optional)
     *
     * If the query is invalid or empty, the `derived_filter_structure` will
     * be null.
     */
    derived_filter_structure: PropTypes.object,

    /**
     * This property represents the current state of `data`
     * on the current page. This property will be updated
     * on paging, sorting, and filtering.
     */
    derived_viewport_data: PropTypes.arrayOf(PropTypes.object),

    /**
     * `derived_viewport_indices` indicates the order in which the original
     * rows appear after being filtered, sorted, and/or paged.
     * `derived_viewport_indices` contains indices for the current page,
     * while `derived_virtual_indices` contains indices across all pages.
     */
    derived_viewport_indices: PropTypes.arrayOf(PropTypes.number),

    /**
     * `derived_viewport_row_ids` lists row IDs in the order they appear
     * after being filtered, sorted, and/or paged.
     * `derived_viewport_row_ids` contains IDs for the current page,
     * while `derived_virtual_row_ids` contains IDs across all pages.
     */
    derived_viewport_row_ids: PropTypes.arrayOf(
        PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    ),

    /**
     * `derived_viewport_selected_rows` represents the indices of the
     * `selected_rows` from the perspective of the `derived_viewport_indices`.
     */
    derived_viewport_selected_rows: PropTypes.arrayOf(PropTypes.number),

    /**
     * `derived_viewport_selected_row_ids` represents the IDs of the
     * `selected_rows` on the currently visible page.
     */
    derived_viewport_selected_row_ids: PropTypes.arrayOf(
        PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    ),

    /**
     * This property represents the visible state of `data`
     * across all pages after the front-end sorting and filtering
     * as been applied.
     */
    derived_virtual_data: PropTypes.arrayOf(PropTypes.object),

    /**
     * `derived_virtual_indices` indicates the order in which the original
     * rows appear after being filtered and sorted.
     * `derived_viewport_indices` contains indices for the current page,
     * while `derived_virtual_indices` contains indices across all pages.
     */
    derived_virtual_indices: PropTypes.arrayOf(PropTypes.number),

    /**
     * `derived_virtual_row_ids` indicates the row IDs in the order in which
     * they appear after being filtered and sorted.
     * `derived_viewport_row_ids` contains IDs for the current page,
     * while `derived_virtual_row_ids` contains IDs across all pages.
     */
    derived_virtual_row_ids: PropTypes.arrayOf(
        PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    ),

    /**
     * `derived_virtual_selected_rows` represents the indices of the
     *  `selected_rows` from the perspective of the `derived_virtual_indices`.
     */
    derived_virtual_selected_rows: PropTypes.arrayOf(PropTypes.number),

    /**
     * `derived_virtual_selected_row_ids` represents the IDs of the
     * `selected_rows` as they appear after filtering and sorting,
     * across all pages.
     */
    derived_virtual_selected_row_ids: PropTypes.arrayOf(
        PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    ),

    /**
     * DEPRECATED
     * Subscribe to [https://github.com/plotly/dash-table/issues/168](https://github.com/plotly/dash-table/issues/168)
     * for updates on the dropdown API.
     */
     dropdown_properties: PropTypes.any
};

DataTable.defaultProps = defaultProps;
DataTable.propTypes = propTypes;
