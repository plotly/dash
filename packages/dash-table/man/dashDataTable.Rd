% Auto-generated: do not edit by hand
\name{dashDataTable}

\alias{dashDataTable}

\title{DataTable component}

\description{

}

\usage{
dashDataTable(active_cell=NULL, columns=NULL, locale_format=NULL,
content_style=NULL, css=NULL, data=NULL, data_previous=NULL,
data_timestamp=NULL, editable=NULL, end_cell=NULL, id=NULL, is_focused=NULL,
merge_duplicate_headers=NULL, n_fixed_columns=NULL, n_fixed_rows=NULL,
row_deletable=NULL, row_selectable=NULL, selected_cells=NULL,
selected_rows=NULL, selected_row_ids=NULL, start_cell=NULL,
style_as_list_view=NULL, pagination_mode=NULL, pagination_settings=NULL,
navigation=NULL, column_conditional_dropdowns=NULL, column_static_dropdown=NULL,
column_static_tooltip=NULL, column_conditional_tooltips=NULL, tooltips=NULL,
tooltip_delay=NULL, tooltip_duration=NULL, filter=NULL, filtering=NULL,
filtering_type=NULL, filtering_types=NULL, sorting=NULL, sorting_type=NULL,
sort_by=NULL, sorting_treat_empty_string_as_none=NULL, style_table=NULL,
style_cell=NULL, style_data=NULL, style_filter=NULL, style_header=NULL,
style_cell_conditional=NULL, style_data_conditional=NULL,
style_filter_conditional=NULL, style_header_conditional=NULL,
virtualization=NULL, derived_filter_structure=NULL, derived_viewport_data=NULL,
derived_viewport_indices=NULL, derived_viewport_row_ids=NULL,
derived_viewport_selected_rows=NULL, derived_viewport_selected_row_ids=NULL,
derived_virtual_data=NULL, derived_virtual_indices=NULL,
derived_virtual_row_ids=NULL, derived_virtual_selected_rows=NULL,
derived_virtual_selected_row_ids=NULL, dropdown_properties=NULL)
}

\arguments{
\item{active_cell}{Lists containing elements 'row', 'column', 'row_id', 'column_id'.
those elements have the following types:
  - row (number; optional)
  - column (number; optional)
  - row_id (string | number; optional)
  - column_id (string | number; optional). The row and column indices and IDs of the currently active cell.}

\item{columns}{List of lists containing elements 'clearable', 'deletable', 'editable', 'editable_name', 'format', 'hidden', 'id', 'name', 'presentation', 'on_change', 'validation', 'options', 'type'.
those elements have the following types:
  - clearable (boolean; optional): if the column is rendered as dropdowns, then the
`clearable` property determines whether or not
the dropdown value can be cleared or not.

note - the name of this property may change in the future,
subscribe to [https://github.com/plotly/dash-table/issues/168](https://github.com/plotly/dash-table/issues/168)
for more information.
  - deletable (boolean | number; optional): if true, the user can delete the column by clicking on a little `x`
button on the column.
if there are merged, multi-header columns then you can choose
which column header row to display the "x" in by
supplying a column row index.
for example, `0` will display the "x" on the first row,
`1` on the second row.
if the "x" appears on a merged column, then clicking on that button
will delete *all* of the merged columns associated with it.
  - editable (boolean; optional): there are two `editable` flags in the table.
this is the  column-level editable flag and there is
also the table-level `editable` flag.

these flags determine whether the contents of the table
are editable or not.

if the column-level `editable` flag is set it overrides
the table-level `editable` flag for that column.
  - editable_name (boolean | number; optional): if true, then the name of this column is editable.
if there are multiple column headers (if `name` is a list of strings),
then `editable_name` can refer to _which_ column header should be
editable by setting it to the column header index.
also, updating the name in a merged column header cell will
update the name of each column.
  - format (optional): the formatting applied to the column's data.

this prop is derived from the [d3-format](https://github.com/d3/d3-format) library specification. apart from
being structured slightly differently (under a single prop), the usage
is the same.

'locale': represents localization specific formatting information
  when left unspecified, will use the default value provided by d3-format.

  'symbol': (default: ['$', '']) a list of two strings representing the
  prefix and suffix symbols. typically used for currency, and implemented using d3's
  currency format, but you can use this for other symbols such as measurement units.
  'decimal': (default: '.') the string used for the decimal separator
  'group': (default: ',') the string used for the groups separator
  'grouping': (default: [3]) a list of integers representing the grouping pattern
  'numerals': a list of ten strings used as replacements for numbers 0-9
  'percent': (default: '%') the string used for the percentage symbol
  'separate_4digits': (default: true) separate integers with 4-digits or less

'nully': a value that will be used in place of the nully value during formatting
  if the value type matches the column type, it will be formatted normally
'prefix': a number representing the si unit to use during formatting
  see `dash_table.format.prefix` enumeration for the list of valid values
'specifier': (default: '') represents the rules to apply when formatting the number

dash_table.formattemplate contains helper functions to rapidly use certain
typical number formats.. format has the following type: dict containing keys 'locale', 'nully', 'prefix', 'specifier'.
those keys have the following types:
  - locale (optional): . locale has the following type: dict containing keys 'symbol', 'decimal', 'group', 'grouping', 'numerals', 'percent', 'separate_4digits'.
those keys have the following types:
  - symbol (list of strings; optional)
  - decimal (string; optional)
  - group (string; optional)
  - grouping (list of numbers; optional)
  - numerals (list of strings; optional)
  - percent (string; optional)
  - separate_4digits (boolean; optional)
  - nully (boolean | number | string | dict | list; optional)
  - prefix (number; optional)
  - specifier (string; optional)
  - hidden (boolean; optional): if true, then the column and its data is hidden.
this can be useful if you want to transport extra
meta data (like a data index) to and from callbacks
but you don't necessarily want to display that data.
  - id (string; required): the `id` of the column.
the column `id` is used to match cells in data
with particular columns.
the `id` is not visible in the table.
  - name (string | list of strings; required): the `name` of the column,
as it appears in the column header.
if `name` is a list of strings, then the columns
will render with multiple headers rows.
  - presentation (a value equal to: 'input', 'dropdown'; optional): the `presentation` to use to display the value.
defaults to 'input' for ['numeric', 'text', 'any'].
  - on_change (optional): the `on_change` behavior of the column for user-initiated modifications.
'action' (default 'coerce'):
 none: do not validate data
 coerce: check if the data corresponds to the destination type and
 attempts to coerce it into the destination type if not
 validate: check if the data corresponds to the destination type (no coercion)

'failure' (default 'reject'): what to do with the value if the action fails
 accept: use the invalid value
 default: replace the provided value with `validation.default`
 reject: do not modify the existing value. on_change has the following type: dict containing keys 'action', 'failure'.
those keys have the following types:
  - action (a value equal to: 'coerce', 'none', 'validate'; optional)
  - failure (a value equal to: 'accept', 'default', 'reject'; optional)
  - validation (optional): the `validation` options.
'allow_null': allow the use of nully values (undefined, null, nan) (default: false)
'default': the default value to apply with on_change.failure = 'default' (default: null)
'allow_yy': `datetime` columns only, allow 2-digit years (default: false).
  if true, we interpret years as ranging from now-70 to now+29 - in 2019
  this is 1949 to 2048 but in 2020 it will be different. if used with
  `action: 'coerce'`, will convert user input to a 4-digit year.. validation has the following type: dict containing keys 'allow_null', 'default', 'allow_yy'.
those keys have the following types:
  - allow_null (boolean; optional)
  - default (boolean | number | string | dict | list; optional)
  - allow_yy (boolean; optional)
  - options (optional): deprecated
please use `column_static_dropdown` instead.
note - dropdown behavior will likely change in the future,
subscribe to [https://github.com/plotly/dash-table/issues/168](https://github.com/plotly/dash-table/issues/168)
for more information.. options has the following type: list of dict containing keys 'label', 'value'.
those keys have the following types:
  - label (number | string; required)
  - value (number | string; required)s
  - type (a value equal to: 'any', 'numeric', 'text', 'datetime'; optional): the data-type of the column's data.
'numeric': represents both floats and ints
'text': represents a string
'datetime': a string representing a date or date-time, in the form:
  'yyyy-mm-dd hh:mm:ss.ssssss' or some truncation thereof. years must
  have 4 digits, unless you use `validation.allow_yy: true`. also
  accepts 't' or 't' between date and time, and allows timezone info
  at the end. to convert these strings to python `datetime` objects,
  use `dateutil.parser.isoparse`. in r use `parse_iso_8601` from the
  `parsedate` library.
  warning: these parsers do not work with 2-digit years, if you use
  `validation.allow_yy: true` and do not coerce to 4-digit years.
  and parsers that do work with 2-digit years may make a different
  guess about the century than we make on the front end.
'any': represents any type of data

defaults to 'any' if undefined.

note: this feature has not been fully implemented.
in the future, it's data types will impact things like
text formatting options in the cell (e.g. display 2 decimals
for a number), filtering options and behavior, and editing
behavior.
stay tuned by following [https://github.com/plotly/dash-table/issues/166](https://github.com/plotly/dash-table/issues/166)s. Columns describes various aspects about each individual column.
`name` and `id` are the only required parameters.}

\item{locale_format}{Lists containing elements 'symbol', 'decimal', 'group', 'grouping', 'numerals', 'percent', 'separate_4digits'.
those elements have the following types:
  - symbol (list of strings; optional)
  - decimal (string; optional)
  - group (string; optional)
  - grouping (list of numbers; optional)
  - numerals (list of strings; optional)
  - percent (string; optional)
  - separate_4digits (boolean; optional). The localization specific formatting information applied to all columns in the table.

This prop is derived from the [d3.formatLocale](https://github.com/d3/d3-format#formatLocale) data structure specification.

When left unspecified, each individual nested prop will default to a pre-determined value.

  'symbol': (default: ['$', '']) a list of two strings representing the
  prefix and suffix symbols. Typically used for currency, and implemented using d3's
  currency format, but you can use this for other symbols such as measurement units.
  'decimal': (default: '.') the string used for the decimal separator
  'group': (default: ',') the string used for the groups separator
  'grouping': (default: [3]) a list of integers representing the grouping pattern
  'numerals': a list of ten strings used as replacements for numbers 0-9
  'percent': (default: '%') the string used for the percentage symbol
  'separate_4digits': (default: True) separate integers with 4-digits or less}

\item{content_style}{A value equal to: 'fit', 'grow'. `content_style` toggles between a set of CSS styles for
two common behaviors:
- `fit`: The table container's width be equal to the width of its content.
- `grow`: The table container's width will grow to be the size of the container.

NOTE - This property will likely change in the future,
subscribe to [https://github.com/plotly/dash-table/issues/176](https://github.com/plotly/dash-table/issues/176)
for more details.}

\item{css}{List of lists containing elements 'selector', 'rule'.
those elements have the following types:
  - selector (string; required)
  - rule (string; required)s. The `css` property is a way to embed CSS selectors and rules
onto the page.
We recommend starting with the `style_*` properties
before using this `css` property.

Example:
[
    {"selector": ".dash-spreadsheet", "rule": 'font-family: "monospace"'}
]}

\item{data}{List of named lists. The contents of the table.
The keys of each item in data should match the column IDs.
Each item can also have an 'id' key, whose value is its row ID. If there
is a column with ID='id' this will display the row ID, otherwise it is
just used to reference the row for selections, filtering, etc.

Example:

[
     {'column-1': 4.5, 'column-2': 'montreal', 'column-3': 'canada'},
     {'column-1': 8, 'column-2': 'boston', 'column-3': 'america'}
]}

\item{data_previous}{List of named lists. The previous state of `data`. `data_previous`
has the same structure as `data` and it will be updated
whenever `data` changes, either through a callback or
by editing the table.
This is a read-only property: setting this property will not
have any impact on the table.}

\item{data_timestamp}{Numeric. The unix timestamp when the data was last edited.
Use this property with other timestamp properties
(such as `n_clicks_timestamp` in `dash_html_components`)
to determine which property has changed within a callback.}

\item{editable}{Logical. If True, then the data in all of the cells is editable.
When `editable` is True, particular columns can be made
uneditable by setting `editable` to `False` inside the `columns`
property.

If False, then the data in all of the cells is uneditable.
When `editable` is False, particular columns can be made
editable by setting `editable` to `True` inside the `columns`
property.}

\item{end_cell}{Lists containing elements 'row', 'column', 'row_id', 'column_id'.
those elements have the following types:
  - row (number; optional)
  - column (number; optional)
  - row_id (string | number; optional)
  - column_id (string | number; optional). When selecting multiple cells
(via clicking on a cell and then shift-clicking on another cell),
`end_cell` represents the row / column coordinates and IDs of the cell
in one of the corners of the region.
`start_cell` represents the coordinates of the other corner.}

\item{id}{Character. The ID of the table.}

\item{is_focused}{Logical. If True, then the `active_cell` is in a focused state.}

\item{merge_duplicate_headers}{Logical. If True, then column headers that have neighbors with duplicate names
will be merged into a single cell.
This will be applied for single column headers and multi-column
headers.}

\item{n_fixed_columns}{Numeric. `n_fixed_columns` will "fix" the set of columns so that
they remain visible when scrolling horizontally across
the unfixed columns. `n_fixed_columns` fixes columns
from left-to-right, so `n_fixed_columns=3` will fix
the first 3 columns.

Note that fixing columns introduces some changes to the
underlying markup of the table and may impact the
way that your columns are rendered or sized.
View the documentation examples to learn more.}

\item{n_fixed_rows}{Numeric. `n_fixed_rows` will "fix" the set of rows so that
they remain visible when scrolling vertically down
the table. `n_fixed_rows` fixes rows
from top-to-bottom, starting from the headers,
so `n_fixed_rows=1` will fix the header row,
`n_fixed_rows=2` will fix the header row and the first row,
or the first two header rows (if there are multiple headers).

Note that fixing rows introduces some changes to the
underlying markup of the table and may impact the
way that your columns are rendered or sized.
View the documentation examples to learn more.}

\item{row_deletable}{Logical. If True, then a `x` will appear next to each `row`
and the user can delete the row.}

\item{row_selectable}{A value equal to: 'single', 'multi', false. If `single`, then the user can select a single row
via a radio button that will appear next to each row.
If `multi`, then the user can select multiple rows
via a checkbox that will appear next to each row.
If `False`, then the user will not be able to select rows
and no additional UI elements will appear.

When a row is selected, its index will be contained
in `selected_rows`.}

\item{selected_cells}{List of lists containing elements 'row', 'column', 'row_id', 'column_id'.
those elements have the following types:
  - row (number; optional)
  - column (number; optional)
  - row_id (string | number; optional)
  - column_id (string | number; optional)s. `selected_cells` represents the set of cells that are selected,
as an array of objects, each item similar to `active_cell`.
Multiple cells can be selected by holding down shift and
clicking on a different cell or holding down shift and navigating
with the arrow keys.}

\item{selected_rows}{List of numerics. `selected_rows` contains the indices of rows that
are selected via the UI elements that appear when
`row_selectable` is `'single'` or `'multi'`.}

\item{selected_row_ids}{List of character | numerics. `selected_row_ids` contains the ids of rows that
are selected via the UI elements that appear when
`row_selectable` is `'single'` or `'multi'`.}

\item{start_cell}{Lists containing elements 'row', 'column', 'row_id', 'column_id'.
those elements have the following types:
  - row (number; optional)
  - column (number; optional)
  - row_id (string | number; optional)
  - column_id (string | number; optional). When selecting multiple cells
(via clicking on a cell and then shift-clicking on another cell),
`start_cell` represents the [row, column] coordinates of the cell
in one of the corners of the region.
`end_cell` represents the coordinates of the other corner.}

\item{style_as_list_view}{Logical. If True, then the table will be styled like a list view
and not have borders between the columns.}

\item{pagination_mode}{A value equal to: 'fe', 'be', true, false. "pagination" refers to a mode of the table where
not all of the rows are displayed at once: only a subset
are displayed (a "page") and the next subset of rows
can viewed by clicking "Next" or "Previous" buttons
at the bottom of the page.

Pagination is used to improve performance: instead of
rendering all of the rows at once (which can be expensive),
we only display a subset of them.

With pagination, we can either page through data that exists
in the table (e.g. page through `10,000` rows in `data` `100` rows at a time)
or we can update the data on-the-fly with callbacks
when the user clicks on the "Previous" or "Next" buttons.
These modes can be toggled with this `pagination_mode` parameter:
- `'fe'` refers to "front-end" paging: passing large data up-front
- `'be'` refers to "back-end" paging: updating the data on the fly via callbacks
- `False` will disable paging, attempting to render all of the data at once
- `True` is the same as `fe`

NOTE: The `fe` and `be` names may change in the future.
Tune in to [https://github.com/plotly/dash-table/issues/167](https://github.com/plotly/dash-table/issues/167) for more.}

\item{pagination_settings}{Lists containing elements 'current_page', 'page_size'.
those elements have the following types:
  - current_page (number; required)
  - page_size (number; required). `pagination_settings` controls the pagination settings
_and_ represents the current state of the pagination UI.
- `page_size` represents the number of rows that will be
displayed on a particular page.
- `current_page` represents which page the user is on.
Use this property to index through data in your callbacks with
backend paging.}

\item{navigation}{Character. DEPRECATED}

\item{column_conditional_dropdowns}{List of lists containing elements 'id', 'dropdowns'.
those elements have the following types:
  - id (string; required)
  - dropdowns (required): . dropdowns has the following type: list of dict containing keys 'condition', 'dropdown'.
those keys have the following types:
  - condition (string; required)
  - dropdown (required): . dropdown has the following type: list of dict containing keys 'label', 'value'.
those keys have the following types:
  - label (string; required)
  - value (number | string; required)sss. `column_conditional_dropdowns` specifies the available options
for dropdowns in various columns and cells.
This property allows you to specify different dropdowns
depending on certain conditions. For example, you may
render different "city" dropdowns in a row depending on the
current value in the "state" column.

NOTE: The naming and the behavior of this option may change
in the future.
Tune in to [https://github.com/plotly/dash-table/issues/168](https://github.com/plotly/dash-table/issues/168)}

\item{column_static_dropdown}{List of lists containing elements 'id', 'dropdown'.
those elements have the following types:
  - id (string; required)
  - dropdown (required): . dropdown has the following type: list of dict containing keys 'label', 'value'.
those keys have the following types:
  - label (string; required)
  - value (number | string; required)ss. `column_static_dropdown` represents the available dropdown
options for different columns.
The `id` property refers to the column ID.
The `dropdown` property refers to the `options` of the
dropdown.

NOTE: The naming and the behavior of this option may change
in the future.
Tune in to [https://github.com/plotly/dash-table/issues/168](https://github.com/plotly/dash-table/issues/168)}

\item{column_static_tooltip}{List with named elements and values of type lists containing elements 'delay', 'duration', 'type', 'value'.
those elements have the following types:
  - delay (number; optional)
  - duration (number; optional)
  - type (a value equal to: 'text', 'markdown'; optional)
  - value (string; required) | character. `column_static_tooltip` represents the tooltip shown
for different columns.
The `property` name refers to the column ID.
The `type` refers to the type of tooltip syntax used
for the tooltip generation. Can either be `markdown`
or `text`. Defaults to `text`.
The `value` refers to the syntax-based content of
the tooltip. This value is required.
The `delay` represents the delay in milliseconds before
the tooltip is shown when hovering a cell. This overrides
the table's `tooltip_delay` property. If set to `null`,
the tooltip will be shown immediately.
The `duration` represents the duration in milliseconds
during which the tooltip is shown when hovering a cell.
This overrides the table's `tooltip_duration` property.
If set to `null`, the tooltip will not disappear.

Alternatively, the value of the property can also be
a plain string. The `text` syntax will be used in
that case.}

\item{column_conditional_tooltips}{List of lists containing elements 'if', 'delay', 'duration', 'type', 'value'.
those elements have the following types:
  - if (required): . if has the following type: dict containing keys 'filter', 'row_index', 'column_id'.
those keys have the following types:
  - filter (string; optional)
  - row_index (number | a value equal to: 'odd', 'even'; optional)
  - column_id (string; optional)
  - delay (number; optional)
  - duration (number; optional)
  - type (a value equal to: 'text', 'markdown'; optional)
  - value (string; required)s. `column_conditional_tooltips` represents the tooltip shown
for different columns and cells.

This property allows you to specify different tooltips for
depending on certain conditions. For example, you may have
different tooltips in the same column based on the value
of a certain data property.

Priority is from first to last defined conditional tooltip
in the list. Higher priority (more specific) conditional
tooltips should be put at the beginning of the list.

The `if` refers to the condition that needs to be fulfilled
in order for the associated tooltip configuration to be
used. If multiple conditions are defined, all conditions
must be met for the tooltip to be used by a cell.

The `if` nested property `column_id` refers to the column
ID that must be matched.
The `if` nested property `row_index` refers to the index
of the row in the source `data`.
The `if` nested property `filter` refers to the query that
must evaluate to True.

The `type` refers to the type of tooltip syntax used
for the tooltip generation. Can either be `markdown`
or `text`. Defaults to `text`.
The `value` refers to the syntax-based content of
the tooltip. This value is required.
The `delay` represents the delay in milliseconds before
the tooltip is shown when hovering a cell. This overrides
the table's `tooltip_delay` property. If set to `null`,
the tooltip will be shown immediately.
The `duration` represents the duration in milliseconds
during which the tooltip is shown when hovering a cell.
This overrides the table's `tooltip_duration` property.
If set to `null`, the tooltip will not disappear.}

\item{tooltips}{List with named elements and values of type list of character | lists containing elements 'delay', 'duration', 'type', 'value'.
those elements have the following types:
  - delay (number; optional)
  - duration (number; optional)
  - type (a value equal to: 'text', 'markdown'; optional)
  - value (string; required)s. `tooltips` represents the tooltip shown
for different columns and cells.
The `property` name refers to the column ID. Each property
contains a list of tooltips mapped to the source `data`
row index.

The `type` refers to the type of tooltip syntax used
for the tooltip generation. Can either be `markdown`
or `text`. Defaults to `text`.
The `value` refers to the syntax-based content of
the tooltip. This value is required.
The `delay` represents the delay in milliseconds before
the tooltip is shown when hovering a cell. This overrides
the table's `tooltip_delay` property. If set to `null`,
the tooltip will be shown immediately.
The `duration` represents the duration in milliseconds
during which the tooltip is shown when hovering a cell.
This overrides the table's `tooltip_duration` property.
If set to `null`, the tooltip will not disappear.

Alternatively, the value of the property can also be
a plain string. The `text` syntax will be used in
that case.}

\item{tooltip_delay}{Numeric. `tooltip_delay` represents the table-wide delay in milliseconds before
the tooltip is shown when hovering a cell. If set to `null`, the tooltip
will be shown immediately.

Defaults to 350.}

\item{tooltip_duration}{Numeric. `tooltip_duration` represents the table-wide duration in milliseconds
during which the tooltip will be displayed when hovering a cell. If
set to `null`, the tooltip will not disappear.

Defaults to 2000.}

\item{filter}{Character. If `filtering` is enabled, then the current filtering
string is represented in this `filter`
property.
NOTE: The shape and structure of this property will
likely change in the future.
Stay tuned in [https://github.com/plotly/dash-table/issues/169](https://github.com/plotly/dash-table/issues/169)}

\item{filtering}{A value equal to: 'fe', 'be', true, false. The `filtering` property controls the behavior of the `filtering` UI.
If `False`, then the filtering UI is not displayed
If `fe` or True, then the filtering UI is displayed and the filtering
happens in the "front-end". That is, it is performed on the data
that exists in the `data` property.
If `be`, then the filtering UI is displayed but it is the
responsibility of the developer to program the filtering
through a callback (where `filter` would be the input
and `data` would be the output).

NOTE - Several aspects of filtering may change in the future,
including the naming of this property.
Tune in to [https://github.com/plotly/dash-table/issues/167](https://github.com/plotly/dash-table/issues/167)}

\item{filtering_type}{A value equal to: 'basic'. UNSTABLE
In the future, there may be several modes of the
filtering UI like `basic`, `advanced`, etc.
Currently, we only `basic`.
NOTE - This will likely change in the future,
subscribe to changes here:
[https://github.com/plotly/dash-table/issues/169](https://github.com/plotly/dash-table/issues/169)}

\item{filtering_types}{List of a value equal to: 'basic's. UNSTABLE
In the future, there may be several modes of the
filtering UI like `basic`, `advanced`, etc
NOTE - This will likely change in the future,
subscribe to changes here:
[https://github.com/plotly/dash-table/issues/169](https://github.com/plotly/dash-table/issues/169)}

\item{sorting}{A value equal to: 'fe', 'be', true, false. The `sorting` property enables data to be
sorted on a per-column basis.
Enabling `sorting` will display a UI element
on each of the columns (up and down arrows).

Sorting can be performed in the "front-end"
with the `fe` (or True) setting or via a callback in your
python "back-end" with the `be` setting.
Clicking on the sort arrows will update the
`sort_by` property.}

\item{sorting_type}{A value equal to: 'single', 'multi'. Sorting can be performed across multiple columns
(e.g. sort by country, sort within each country,
 sort by year) or by a single column.

NOTE - With multi-column sort, it's currently
not possible to determine the order in which
the columns were sorted through the UI.
See [https://github.com/plotly/dash-table/issues/170](https://github.com/plotly/dash-table/issues/170)}

\item{sort_by}{List of lists containing elements 'column_id', 'direction'.
those elements have the following types:
  - column_id (string | number; required)
  - direction (a value equal to: 'asc', 'desc'; required)s. `sort_by` describes the current state
of the sorting UI.
That is, if the user clicked on the sort arrow
of a column, then this property will be updated
with the column ID and the direction
(`asc` or `desc`) of the sort.
For multi-column sorting, this will be a list of
sorting parameters, in the order in which they were
clicked.}

\item{sorting_treat_empty_string_as_none}{Logical. If False, then empty strings (`''`) are considered
valid values (they will appear first when sorting ascending).
If True, empty strings will be ignored, causing these cells to always
appear last.}

\item{style_table}{Named list. CSS styles to be applied to the outer `table` container.

This is commonly used for setting properties like the
width or the height of the table.}

\item{style_cell}{Named list. CSS styles to be applied to each individual cell of the table.

This includes the header cells, the `data` cells, and the filter
cells.}

\item{style_data}{Named list. CSS styles to be applied to each individual data cell.

That is, unlike `style_cell`, it excludes the header and filter cells.}

\item{style_filter}{Named list. CSS styles to be applied to the filter cells.

Note that this may change in the future as we build out a
more complex filtering UI.}

\item{style_header}{Named list. CSS styles to be applied to each individual header cell.

That is, unlike `style_cell`, it excludes the `data` and filter cells.}

\item{style_cell_conditional}{List of lists containing elements 'if'.
those elements have the following types:
  - if (optional): . if has the following type: dict containing keys 'column_id', 'column_type'.
those keys have the following types:
  - column_id (string | number; optional)
  - column_type (a value equal to: 'any', 'numeric', 'text', 'datetime'; optional)s. Conditional CSS styles for the cells.

This can be used to apply styles to cells on a per-column basis.}

\item{style_data_conditional}{List of lists containing elements 'if'.
those elements have the following types:
  - if (optional): . if has the following type: dict containing keys 'column_id', 'column_type', 'filter', 'row_index'.
those keys have the following types:
  - column_id (string | number; optional)
  - column_type (a value equal to: 'any', 'numeric', 'text', 'datetime'; optional)
  - filter (string; optional)
  - row_index (number | a value equal to: 'odd', 'even'; optional)s. Conditional CSS styles for the data cells.

This can be used to apply styles to data cells on a per-column basis.}

\item{style_filter_conditional}{List of lists containing elements 'if'.
those elements have the following types:
  - if (optional): . if has the following type: dict containing keys 'column_id', 'column_type'.
those keys have the following types:
  - column_id (string | number; optional)
  - column_type (a value equal to: 'any', 'numeric', 'text', 'datetime'; optional)s. Conditional CSS styles for the filter cells.

This can be used to apply styles to filter cells on a per-column basis.}

\item{style_header_conditional}{List of lists containing elements 'if'.
those elements have the following types:
  - if (optional): . if has the following type: dict containing keys 'column_id', 'column_type', 'header_index'.
those keys have the following types:
  - column_id (string | number; optional)
  - column_type (a value equal to: 'any', 'numeric', 'text', 'datetime'; optional)
  - header_index (number | a value equal to: 'odd', 'even'; optional)s. Conditional CSS styles for the header cells.

This can be used to apply styles to header cells on a per-column basis.}

\item{virtualization}{Logical. This property tells the table to use virtualization when rendering.

Assumptions are that:
- the width of the columns is fixed
- the height of the rows is always the same
- runtime styling changes will not affect width and height vs. first rendering}

\item{derived_filter_structure}{Named list. This property represents the current structure of
`filter` as a tree structure. Each node of the
query structure have:
- type (string; required)
  - 'open-block'
  - 'logical-operator'
  - 'relational-operator'
  - 'unary-operator'
  - 'expression'
- subType (string; optional)
  - 'open-block': '()'
  - 'logical-operator': '&&', '||'
  - 'relational-operator': '=', '>=', '>', '<=', '<', '!=', 'contains'
  - 'unary-operator': '!', 'is bool', 'is even', 'is nil', 'is num', 'is object', 'is odd', 'is prime', 'is str'
  - 'expression': 'value', 'field'
- value (any)
  - 'expression, value': passed value
  - 'expression, field': the field/prop name

- block (nested query structure; optional)
- left (nested query structure; optional)
- right (nested query structure; optional)

If the query is invalid or empty, the `derived_filter_structure` will
be null.}

\item{derived_viewport_data}{List of named lists. This property represents the current state of `data`
on the current page. This property will be updated
on paging, sorting, and filtering.}

\item{derived_viewport_indices}{List of numerics. `derived_viewport_indices` indicates the order in which the original
rows appear after being filtered, sorted, and/or paged.
`derived_viewport_indices` contains indices for the current page,
while `derived_virtual_indices` contains indices across all pages.}

\item{derived_viewport_row_ids}{List of character | numerics. `derived_viewport_row_ids` lists row IDs in the order they appear
after being filtered, sorted, and/or paged.
`derived_viewport_row_ids` contains IDs for the current page,
while `derived_virtual_row_ids` contains IDs across all pages.}

\item{derived_viewport_selected_rows}{List of numerics. `derived_viewport_selected_rows` represents the indices of the
`selected_rows` from the perspective of the `derived_viewport_indices`.}

\item{derived_viewport_selected_row_ids}{List of character | numerics. `derived_viewport_selected_row_ids` represents the IDs of the
`selected_rows` on the currently visible page.}

\item{derived_virtual_data}{List of named lists. This property represents the visible state of `data`
across all pages after the front-end sorting and filtering
as been applied.}

\item{derived_virtual_indices}{List of numerics. `derived_virtual_indices` indicates the order in which the original
rows appear after being filtered and sorted.
`derived_viewport_indices` contains indices for the current page,
while `derived_virtual_indices` contains indices across all pages.}

\item{derived_virtual_row_ids}{List of character | numerics. `derived_virtual_row_ids` indicates the row IDs in the order in which
they appear after being filtered and sorted.
`derived_viewport_row_ids` contains IDs for the current page,
while `derived_virtual_row_ids` contains IDs across all pages.}

\item{derived_virtual_selected_rows}{List of numerics. `derived_virtual_selected_rows` represents the indices of the
 `selected_rows` from the perspective of the `derived_virtual_indices`.}

\item{derived_virtual_selected_row_ids}{List of character | numerics. `derived_virtual_selected_row_ids` represents the IDs of the
`selected_rows` as they appear after filtering and sorting,
across all pages.}

\item{dropdown_properties}{Logical | numeric | character | named list | unnamed list. DEPRECATED
Subscribe to [https://github.com/plotly/dash-table/issues/168](https://github.com/plotly/dash-table/issues/168)
for updates on the dropdown API.}
}

