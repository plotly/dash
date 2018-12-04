# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DataTable(Component):
    """A DataTable component.


Keyword arguments:
- active_cell (list; optional): The [row, column] index of which cell is currently
active.
- columns (list; optional): Columns describes various aspects about each individual column.
`name` and `id` are the only required parameters.
- content_style (a value equal to: 'fit', 'grow'; optional): `content_style` toggles between a set of CSS styles for
two common behaviors:
- `fit`: The table container's width be equal to the width of its content.
- `grow`: The table container's width will grow to be the size of the container.

NOTE - This property will likely change in the future,
subscribe to [https://github.com/plotly/dash-table/issues/176](https://github.com/plotly/dash-table/issues/176)
for more details.
- css (list; optional): The `css` property is a way to embed CSS selectors and rules
onto the page.
We recommend starting with the `style_*` properties
before using this `css` property.

Example:
[
    {"selector": ".dash-spreadsheet", "rule": 'font-family: "monospace"'}
]
- data (list; optional): The contents of the table.
The keys of each item in data should match the column IDs.
Example:

[
     {'column-1': 4.5, 'column-2': 'montreal', 'column-3': 'canada'},
     {'column-1': 8, 'column-2': 'boston', 'column-3': 'america'}
]
- data_previous (list; optional): The previous state of `data`. `data_previous`
has the same structure as `data` and it will be updated
whenever `data` changes, either through a callback or
by editing the table.
This is a read-only property: setting this property will not
have any impact on the table.
- data_timestamp (number; optional): The unix timestamp when the data was last edited.
Use this property with other timestamp properties
(such as `n_clicks_timestamp` in `dash_html_components`)
to determine which property has changed within a callback.
- editable (boolean; optional): If True, then the data in all of the cells is editable.
When `editable` is True, particular columns can be made
uneditable by setting `editable` to `False` inside the `columns`
property.

If False, then the data in all of the cells is uneditable.
When `editable` is False, particular columns can be made
editable by setting `editable` to `True` inside the `columns`
property.
- end_cell (list; optional): When selecting multiple cells
(via clicking on a cell and then shift-clicking on another cell),
`end_cell` represents the [row, column] coordinates of the cell
in one of the corners of the region.
`start_cell` represents the coordinates of the other corner.
- id (string; optional): The ID of the table.
- is_focused (boolean; optional): If True, then the `active_cell` is in a focused state.
- merge_duplicate_headers (boolean; optional): If True, then column headers that have neighbors with duplicate names
will be merged into a single cell.
This will be applied for single column headers and multi-column
headers.
- n_fixed_columns (number; optional): `n_fixed_columns` will "fix" the set of columns so that
they remain visible when scrolling horizontally across
the unfixed columns. `n_fixed_columns` fixes columns
from left-to-right, so `n_fixed_columns=3` will fix
the first 3 columns.

Note that fixing columns introduces some changes to the
underlying markup of the table and may impact the
way that your columns are rendered or sized.
View the documentation examples to learn more.
- n_fixed_rows (number; optional): `n_fixed_rows` will "fix" the set of rows so that
they remain visible when scrolling vertically down
the table. `n_fixed_rows` fixes rows
from top-to-bottom, starting from the headers,
so `n_fixed_rows=1` will fix the header row,
`n_fixed_rows=2` will fix the header row and the first row,
or the first two header rows (if there are multiple headers).

Note that fixing rows introduces some changes to the
underlying markup of the table and may impact the
way that your columns are rendered or sized.
View the documentation examples to learn more.
- row_deletable (boolean; optional): If True, then a `x` will appear next to each `row`
and the user can delete the row.
- row_selectable (a value equal to: 'single', 'multi', false; optional): If `single`, then the user can select a single row
via a radio button that will appear next to each row.
If `multi`, then the user can select multiple rows
via a checkbox that will appear next to each row.
If `False`, then the user will not be able to select rows
and no additional UI elements will appear.

When a row is selected, its index will be contained
in `selected_rows`.
- selected_cells (list; optional): `selected_cells` represents the set of cells that are selected.
This is similar to `active_cell` except that it contains multiple
cells. Multiple cells can be selected by holding down shift and
clicking on a different cell or holding down shift and navigating
with the arrow keys.

NOTE - This property may change in the future, subscribe to
[https://github.com/plotly/dash-table/issues/177](https://github.com/plotly/dash-table/issues/177)
for more details.
- selected_rows (list; optional): `selected_rows` contains the indices of the rows that
are selected via the UI elements that appear when
`row_selectable` is `'single'` or `'multi'`.
- start_cell (list; optional): When selecting multiple cells
(via clicking on a cell and then shift-clicking on another cell),
`start_cell` represents the [row, column] coordinates of the cell
in one of the corners of the region.
`end_cell` represents the coordinates of the other corner.
- style_as_list_view (boolean; optional): If True, then the table will be styled like a list view
and not have borders between the columns.
- pagination_mode (a value equal to: 'fe', 'be', true, false; optional): "pagination" refers to a mode of the table where
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
Tune in to [https://github.com/plotly/dash-table/issues/167](https://github.com/plotly/dash-table/issues/167) for more.
- pagination_settings (optional): `pagination_settings` controls the pagination settings
_and_ represents the current state of the pagination UI.
- `page_size` represents the number of rows that will be
displayed on a particular page.
- `current_page` represents which page the user is on.
Use this property to index through data in your callbacks with
backend paging.
- `displayed_pages` is DEPRECATED.. pagination_settings has the following type: dict containing keys 'displayed_pages', 'current_page', 'page_size'.
Those keys have the following types: 
  - displayed_pages (number; required)
  - current_page (number; required)
  - page_size (number; required)
- navigation (string; optional): DEPRECATED
- column_conditional_dropdowns (list; optional): `column_conditional_dropdowns` specifies the available options
for dropdowns in various columns and cells.
This property allows you to specify different dropdowns
depending on certain conditions. For example, you may
render different "city" dropdowns in a row depending on the
current value in the "state" column.

NOTE: The naming and the behavior of this option may change
in the future.
Tune in to [https://github.com/plotly/dash-table/issues/168](https://github.com/plotly/dash-table/issues/168)
- column_static_dropdown (list; optional): `column_static_dropdown` represents the available dropdown
options for different columns.
The `id` property refers to the column ID.
The `dropdown` property refers to the `options` of the
dropdown.

NOTE: The naming and the behavior of this option may change
in the future.
Tune in to [https://github.com/plotly/dash-table/issues/168](https://github.com/plotly/dash-table/issues/168)
- filtering (a value equal to: 'fe', 'be', true, false; optional): The `filtering` property controls the behavior of the `filtering` UI.
If `False`, then the filtering UI is not displayed
If `fe` or True, then the filtering UI is displayed and the filtering
happens in the "front-end". That is, it is performed on the data
that exists in the `data` property.
If `be`, then the filtering UI is displayed but it is the
responsibility of the developer to program the filtering
through a callback (where `filtering_settings` would be the input
and `data` would be the output).

NOTE - Several aspects of filtering may change in the future,
including the naming of this property.
Tune in to [https://github.com/plotly/dash-table/issues/167](https://github.com/plotly/dash-table/issues/167)
- filtering_settings (string; optional): If `filtering` is enabled, then the current filtering
string is represented in this `filtering_settings`
property.
NOTE: The shape and structure of this property will
likely change in the future.
Stay tuned in [https://github.com/plotly/dash-table/issues/169](https://github.com/plotly/dash-table/issues/169)
- filtering_type (a value equal to: 'basic'; optional): UNSTABLE
In the future, there may be several modes of the
filtering UI like `basic`, `advanced`, etc.
Currently, we only `basic`.
NOTE - This will likely change in the future,
subscribe to changes here:
[https://github.com/plotly/dash-table/issues/169](https://github.com/plotly/dash-table/issues/169)
- filtering_types (list; optional): UNSTABLE
In the future, there may be several modes of the
filtering UI like `basic`, `advanced`, etc
NOTE - This will likely change in the future,
subscribe to changes here:
[https://github.com/plotly/dash-table/issues/169](https://github.com/plotly/dash-table/issues/169)
- sorting (a value equal to: 'fe', 'be', true, false; optional): The `sorting` property enables data to be
sorted on a per-column basis.
Enabling `sorting` will display a UI element
on each of the columns (up and down arrows).

Sorting can be performed in the "front-end"
with the `fe` (or True) setting or via a callback in your
python "back-end" with the `be` setting.
Clicking on the sort arrows will update the
`sorting_settings` property.
- sorting_type (a value equal to: 'single', 'multi'; optional): Sorting can be performed across multiple columns
(e.g. sort by country, sort within each country,
 sort by year) or by a single column.

NOTE - With multi-column sort, it's currently
not possible to determine the order in which
the columns were sorted through the UI.
See [https://github.com/plotly/dash-table/issues/170](https://github.com/plotly/dash-table/issues/170)
- sorting_settings (list; optional): `sorting_settings` describes the current state
of the sorting UI.
That is, if the user clicked on the sort arrow
of a column, then this property will be updated
with the column ID and the direction
(`asc` or `desc`) of the sort.
For multi-column sorting, this will be a list of
sorting parameters, in the order in which they were
clicked.
- sorting_treat_empty_string_as_none (boolean; optional): If False, then empty strings (`''`) are considered
valid values (they will appear first when sorting ascending).
If True, empty strings will be ignored, causing these cells to always
appear last.
- style_table (dict; optional): CSS styles to be applied to the outer `table` container.

This is commonly used for setting properties like the
width or the height of the table.
- style_cell (dict; optional): CSS styles to be applied to each individual cell of the table.

This includes the header cells, the `data` cells, and the filter
cells.
- style_data (dict; optional): CSS styles to be applied to each individual data cell.

That is, unlike `style_cell`, it excludes the header and filter cells.
- style_filter (dict; optional): CSS styles to be applied to the filter cells.

Note that this may change in the future as we build out a
more complex filtering UI.
- style_header (dict; optional): CSS styles to be applied to each individual header cell.

That is, unlike `style_cell`, it excludes the `data` and filter cells.
- style_cell_conditional (list; optional): Conditional CSS styles for the cells.

This can be used to apply styles to cells on a per-column basis.
- style_data_conditional (list; optional): Conditional CSS styles for the data cells.

This can be used to apply styles to data cells on a per-column basis.
- style_filter_conditional (list; optional): Conditional CSS styles for the filter cells.

This can be used to apply styles to filter cells on a per-column basis.
- style_header_conditional (list; optional): Conditional CSS styles for the header cells.

This can be used to apply styles to header cells on a per-column basis.
- virtualization (boolean; optional): This property tells the table to use virtualization when rendering.

Assumptions are that:
- the width of the columns is fixed
- the height of the rows is always the same
- runtime styling changes will not affect width and height vs. first rendering
- derived_viewport_data (list; optional): This property represents the current state of `data`
on the current page. This property will be updated
on paging, sorting, and filtering.
- derived_viewport_indices (list; optional): `derived_viewport_indices` indicates the order in which the original
rows appear after being filtered, sorted, and/or paged.
`derived_viewport_indices` contains indices for the current page,
while `derived_virtual_indices` contains indices for across all pages.
- derived_viewport_selected_rows (list; optional): `derived_viewport_selected_rows` represents the indices of the
 `selected_rows` from the perspective of the `derived_viewport_indices`.
- derived_virtual_data (list; optional): This property represents the visible state of `data`
across all pages after the front-end sorting and filtering
as been applied.
- derived_virtual_indices (list; optional): `derived_viewport_indices` indicates the order in which the original
rows appear after being filtered, sorted, and/or paged.
`derived_viewport_indices` contains indices for the current page,
while `derived_virtual_indices` contains indices for across all pages.
- derived_virtual_selected_rows (list; optional): `derived_virtual_selected_rows` represents the indices of the
 `selected_rows` from the perspective of the `derived_virtual_indices`.
- dropdown_properties (boolean | number | string | dict | list; optional): DEPRECATED
Subscribe to [https://github.com/plotly/dash-table/issues/168](https://github.com/plotly/dash-table/issues/168)
for updates on the dropdown API.

Available events: """
    @_explicitize_args
    def __init__(self, active_cell=Component.UNDEFINED, columns=Component.UNDEFINED, content_style=Component.UNDEFINED, css=Component.UNDEFINED, data=Component.UNDEFINED, data_previous=Component.UNDEFINED, data_timestamp=Component.UNDEFINED, editable=Component.UNDEFINED, end_cell=Component.UNDEFINED, id=Component.UNDEFINED, is_focused=Component.UNDEFINED, merge_duplicate_headers=Component.UNDEFINED, n_fixed_columns=Component.UNDEFINED, n_fixed_rows=Component.UNDEFINED, row_deletable=Component.UNDEFINED, row_selectable=Component.UNDEFINED, selected_cells=Component.UNDEFINED, selected_rows=Component.UNDEFINED, start_cell=Component.UNDEFINED, style_as_list_view=Component.UNDEFINED, pagination_mode=Component.UNDEFINED, pagination_settings=Component.UNDEFINED, navigation=Component.UNDEFINED, column_conditional_dropdowns=Component.UNDEFINED, column_static_dropdown=Component.UNDEFINED, filtering=Component.UNDEFINED, filtering_settings=Component.UNDEFINED, filtering_type=Component.UNDEFINED, filtering_types=Component.UNDEFINED, sorting=Component.UNDEFINED, sorting_type=Component.UNDEFINED, sorting_settings=Component.UNDEFINED, sorting_treat_empty_string_as_none=Component.UNDEFINED, style_table=Component.UNDEFINED, style_cell=Component.UNDEFINED, style_data=Component.UNDEFINED, style_filter=Component.UNDEFINED, style_header=Component.UNDEFINED, style_cell_conditional=Component.UNDEFINED, style_data_conditional=Component.UNDEFINED, style_filter_conditional=Component.UNDEFINED, style_header_conditional=Component.UNDEFINED, virtualization=Component.UNDEFINED, derived_viewport_data=Component.UNDEFINED, derived_viewport_indices=Component.UNDEFINED, derived_viewport_selected_rows=Component.UNDEFINED, derived_virtual_data=Component.UNDEFINED, derived_virtual_indices=Component.UNDEFINED, derived_virtual_selected_rows=Component.UNDEFINED, dropdown_properties=Component.UNDEFINED, **kwargs):
        self._prop_names = ['active_cell', 'columns', 'content_style', 'css', 'data', 'data_previous', 'data_timestamp', 'editable', 'end_cell', 'id', 'is_focused', 'merge_duplicate_headers', 'n_fixed_columns', 'n_fixed_rows', 'row_deletable', 'row_selectable', 'selected_cells', 'selected_rows', 'start_cell', 'style_as_list_view', 'pagination_mode', 'pagination_settings', 'navigation', 'column_conditional_dropdowns', 'column_static_dropdown', 'filtering', 'filtering_settings', 'filtering_type', 'filtering_types', 'sorting', 'sorting_type', 'sorting_settings', 'sorting_treat_empty_string_as_none', 'style_table', 'style_cell', 'style_data', 'style_filter', 'style_header', 'style_cell_conditional', 'style_data_conditional', 'style_filter_conditional', 'style_header_conditional', 'virtualization', 'derived_viewport_data', 'derived_viewport_indices', 'derived_viewport_selected_rows', 'derived_virtual_data', 'derived_virtual_indices', 'derived_virtual_selected_rows', 'dropdown_properties']
        self._type = 'DataTable'
        self._namespace = 'dash_table'
        self._valid_wildcard_attributes =            []
        self.available_events = []
        self.available_properties = ['active_cell', 'columns', 'content_style', 'css', 'data', 'data_previous', 'data_timestamp', 'editable', 'end_cell', 'id', 'is_focused', 'merge_duplicate_headers', 'n_fixed_columns', 'n_fixed_rows', 'row_deletable', 'row_selectable', 'selected_cells', 'selected_rows', 'start_cell', 'style_as_list_view', 'pagination_mode', 'pagination_settings', 'navigation', 'column_conditional_dropdowns', 'column_static_dropdown', 'filtering', 'filtering_settings', 'filtering_type', 'filtering_types', 'sorting', 'sorting_type', 'sorting_settings', 'sorting_treat_empty_string_as_none', 'style_table', 'style_cell', 'style_data', 'style_filter', 'style_header', 'style_cell_conditional', 'style_data_conditional', 'style_filter_conditional', 'style_header_conditional', 'virtualization', 'derived_viewport_data', 'derived_viewport_indices', 'derived_viewport_selected_rows', 'derived_virtual_data', 'derived_virtual_indices', 'derived_virtual_selected_rows', 'dropdown_properties']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DataTable, self).__init__(**args)

    def __repr__(self):
        if(any(getattr(self, c, None) is not None
               for c in self._prop_names
               if c is not self._prop_names[0])
           or any(getattr(self, c, None) is not None
                  for c in self.__dict__.keys()
                  if any(c.startswith(wc_attr)
                  for wc_attr in self._valid_wildcard_attributes))):
            props_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self._prop_names
                                      if getattr(self, c, None) is not None])
            wilds_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self.__dict__.keys()
                                      if any([c.startswith(wc_attr)
                                      for wc_attr in
                                      self._valid_wildcard_attributes])])
            return ('DataTable(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'DataTable(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
