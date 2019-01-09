# Change Log for dash-table
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]
### Fixed
- Regression, misaligned header [#324](https://github.com/plotly/dash-core/issues/324)
### Maintenance
- Test with head of both Dash v0.x and Dash v1.x [#20](https://github.com/plotly/dash-core/issues/20)

## [3.1.11] - 2018-12-10
### Fixed
- Selection, navigation, copy from readonly cell [#276](https://github.com/plotly/dash-table/issues/276)

## [3.1.10] - 2018-12-10
### Removed
- Deprecated nested property 'displayed_pages' from 'pagination_settings' [#275](https://github.com/plotly/dash-table/issues/275)

## [3.1.9] - 2018-12-06
### Added
- Source map [#284](https://github.com/plotly/dash-table/issues/284)
    Related Dash issue [#480](https://github.com/plotly/dash/issues/480)
### Changed
- Refactoring in preparation for data types [#280](https://github.com/plotly/dash-table/issues/280)

## [3.1.8] - 2018-12-04
### Added
- Virtualization [#234](https://github.com/plotly/dash-table/issues/234)
### Fixed
- Linting correctly applied to all code [#254](https://github.com/plotly/dash-table/issues/254)
### Changed
- Update dependencies [#278](https://github.com/plotly/dash-table/pull/278)
- Update dependencies [#274](https://github.com/plotly/dash-table/pull/274)
- Update dependencies [#251](https://github.com/plotly/dash-table/pull/251)


## [3.1.7] - 2018-11-19
### Fixed
- Visual offset with vertical scroll [#216](https://github.com/plotly/dash-table/issues/216)

## [3.1.6] - 2018-11-15
### Changed
- Generate python components classes for IDE support [#243](https://github.com/plotly/dash-table/pull/243)

## [3.1.5] - 2018-11-09
### Fixed
- Fix python package regression [#235](https://github.com/plotly/dash-table/issues/235)

## [3.1.4] - 2018-11-06
### Added
- New derived props for `selected_rows` [#147](https://github.com/plotly/dash-table/issues/147)
- Package library the UMD way [#212](https://github.com/plotly/dash-table/issues/212)

## [3.1.3] - 2018-11-05
### Fixed
- Fix load in IE 11 [#217](https://github.com/plotly/dash-table/issues/217)

## [3.1.2] - 2018-11-02
### Fixed
The version in the package didn't get updated.

## [3.1.1] - 2018-11-02
### Fixed
The remote URL path for the bundle was incorrect.

## [3.1.0] - 2018-11-02
- 3.1.0 (Alpha) Release of the Dash Table

## [3.1.0-rc21] - 2018-11-02
### Fixed
- Fire submit when pressing enter key in `IsolatedInput`. Fixes issue [#194](https://github.com/plotly/dash-table/issues/194)

## [3.1.0-rc20] - 2018-11-01
### Fixed
- Fix performance degradation on load [#208](https://github.com/plotly/dash-table/pull/208) [#200](https://github.com/plotly/dash-table/pull/200) [#198](https://github.com/plotly/dash-table/issues/198)

## [3.1.0-rc19] - 2018-11-01
### Changed
- Change default styles [#193](https://github.com/plotly/dash-table/pull/193) [#150](https://github.com/plotly/dash-table/issues/150)
    - prop `content_style` defaults to 'grow' instead of 'fit'
    - prop `style_table` width nested property defaults to '100%' if not provided
- Change cell styling and filter display [#196](https://github.com/plotly/dash-table/pull/196) [#150](https://github.com/plotly/dash-table/issues/150)
    - uneditable cells can be clicked & navigated, the mouse cursor is the default one
    - filter inputs have a placeholder that is visible on hover and focus
    - first filter input placeholder is always visible

## [3.1.0-rc18] - 2018-10-31
### Changed
- Rename table component to DataTable [#187](https://github.com/plotly/dash-table/pull/187) [#154](https://github.com/plotly/dash-table/issues/154)

## [3.1.0-rc17] - 2018-10-31
### Fixed
- Fix install on Linux [#184](https://github.com/plotly/dash-table/pull/184) [#137](https://github.com/plotly/dash-table/issues/137)

## [3.1.0-rc16] - 2018-10-30
### Fixed
- Fix copy/paste behavior when copying rows larger than data [#180](https://github.com/plotly/dash-table/pull/180) [#142](https://github.com/plotly/dash-table/issues/142)

## [3.1.0-rc15] - 2018-10-30
### Changed
- Column 'editable' prop takes precedence over table 'editable' prop[#182](https://github.com/plotly/dash-table/pull/182) [#175](https://github.com/plotly/dash-table/issues/175)

## [3.1.0-rc14] - 2018-10-30
### Changed
- Rename sorting_settings columnId -> column_id [#183](https://github.com/plotly/dash-table/pull/183) [#171](https://github.com/plotly/dash-table/issues/171)

## [3.1.0-rc13] - 2018-10-30
### Changed
- Allow keyboard navigation on focused input [#172](https://github.com/plotly/dash-table/pull/172) [#141](https://github.com/plotly/dash-table/issues/141) [#143](https://github.com/plotly/dash-table/issues/143)

## [3.1.0-rc12] - 2018-10-29
### Changed
- Rename selected_cell -> selected_cells [#181](https://github.com/plotly/dash-table/pull/181) [#177](https://github.com/plotly/dash-table/issues/177)

## [3.1.0-rc11]
### Fixed
- Fix regressions linked to the style_as_list_view feature / prop [#179](https://github.com/plotly/dash-table/pull/179)

## [3.1.0-rc10]
### Changed
- Improved props docstrings [#163](https://github.com/plotly/dash-table/issues/163)

## [3.1.0-rc9]
### Changed
- Sort ascending on first click [#164](https://github.com/plotly/dash-table/pull/164) [#118](https://github.com/plotly/dash-table/issues/118)
    - Flips icons displayed so that they are pointing up on ascending and down on descending.

## [3.1.0-rc8]
### Changed
- Improve props typing [#158](https://github.com/plotly/dash-table/pulls/158) [#143](https://github.com/plotly/dash-table/issues/143)

## [3.1.0-rc7]
### Changed
- Make table id optional (generate random one if needed) [#155](https://github.com/plotly/dash-table/pulls/155) [#139](https://github.com/plotly/dash-table/issues/139)

## [3.1.0-rc6]
### Added
- Styling API refactoring

    - Remove column width / maxWidth / minWidth
    - Rename property table_style to css

    Cell: All table cells
    Data: All data driven cells (no operations, headers, filters)
    Filter: All basic filter cells
    Header: All header cells

    Priority
    Data: style_data_conditional > style_data > style_cell_conditional > style_cell
    Filter: style_filter_conditional > style_filter > style_cell_conditional > style_cell
    Header: style_header_conditional > style_header > style_cell_conditional > style_cell

    Merge Logic
    Only properties defined at a higher priority level will override properties
    defined at lower priority levels. For example if A is applied then B, A+B will be..

    A = {
        background_color: 'floralwhite',
        color: 'red',
        font_type: 'monospace',
        width: 100
    }

    B = {
        color: 'black',
        font_size: 22
    }

    A+B = {
        background_color: 'floralwhite', // from A, not overriden
        color: 'black', // from B, A overriden
        font_size: 22, // from B
        font_type: 'monospace', // from A
        width: 100 // from A
    }

    - Add new property style_table of form
        { ...CSSProperties }
    - Add new property style_cell of form
        { ...CSSProperties }
    - Add new property style_data of form
        { ...CSSProperties }
    - Add new property style_filter of form
        { ...CSSProperties }
    - Add new property style_header of form
        { ...CSSProperties }
    - Add new property style_cell_conditional of form
        [{
            if: { column_id: string | number },
            ...CSSProperties
        }]
    - Add new property style_data_conditional of form
        [{
            if: { column_id: string | number, filter: string, row_index: number | 'odd' | 'even' },
            ...CSSProperties
        }]
    - Add new property style_filter_conditional of form
        [{
            if: { column_id: string | number },
            ...CSSProperties
        }]
    - Add new property style_header_conditional of form
        [{
            if: { column_id: string | number, header_index: number | 'odd' | 'even' },
            ...CSSProperties
        }]
    - All CSSProperties are supported in kebab-cass, camelCase and snake_case

### Changed
- Renaming 'dataframe' props to 'data'
    dataframe -> data
    dataframe_previous -> data_previous
    dataframe_timestamp -> data_timestamp
    derived_virtual_dataframe -> derived_virtual_data
    derived_viewport_dataframe -> derived_viewport_data

## [3.1.0-rc5]
### Fixed
- Tests and fixes for editable/readonly [#134](https://github.com/plotly/dash-table/pull/134) [#132](https://github.com/plotly/dash-table/issues/132)

## [3.1.0-rc4]
### Added
Columns width percentage and default (fit to content) support
- Added prop content_style that takes values 'fit' or 'grow' (Default='fit')
- Added width percentage support
- Modified default column behavior from fixed width to 'fit content'
- Modified width, min-width, max-width interaction on columns

Width percentage

    Columns can now accept '%' width, minWidth, maxWidth

    For the percentages to have meaning, the dash-table must be forced to have a width and the content of the dash-table must be forced to grow to fill the available space made available by the container (by default the table is only as big as it needs to be).

    To use percentage-based column widths, add:

    - content style
        content_style='grow'

    - table style (example)
        table_style=[{ selector: '.dash-spreadsheet', rule: 'width: 100%; max-width: 100%' }]

    - column with %-based width
        columns=[{
            id: 'column',
            width: '40%'
        }]

Default column width

    Columns now default to 'fit to content' when no width is defined
    Note: If pagination is used or the dataframe modified, the column width will be re-evaluated on each modification.

Interaction between width, min-width and max-width

    Column min-width and max-width do not default to width value is not defined.

## [3.1.0-rc3]
### Fixed
- Miscellaneous fixes for pagination, virtual df and viewport df [#112](https://github.com/plotly/dash-table/pull/112)

## [3.1.0-rc2]
### Changed
- 1 new internal facing derived/controlled property:
    columns: Columns -> columns: VisibleColumns
    Gets rid of conditional processing for hidden columns in the cell and header factories as well as in navigation/selection handlers

Clean up column offsets
- A bunch of offsets were introduced to the table in the previous development cycle (2.x -> 3.0). Turns out these offsets are neither useful or necessary


Validate compatibility of filtering, sorting, pagination

External facing classes and attributes
- (ATTRIBUTE) data-dash-column=<columnId>

    .dash-cell,
    .dash-header {
        &[data-dash-column='ticker'] {
            // styling
        }
    }

- (CLASS) dash-cell
- (CLASS) dash-header

- (CLASS) dash-delete-cell
- (CLASS) dash-delete-header
- (CLASS) dash-select-cell
- (CLASS) dash-select-header

- (CLASS) dash-cell-value

- (CLASS) dash-freeze-left
- (CLASS) dash-freeze-top
- (CLASS) dash-spreadsheet
- (CLASS) dash-spreadsheet-container
- (CLASS) dash-spreadsheet-inner

## [3.1.0-rc1]
### Added
Version 3.1 of the Dash-Table builds upon the 3.0 table and solidifies the external facing API of the table
- introducing the notion of derived properties
- virtual and viewport dataframe and indices for more flexibility
- code refactoring to simplify and improve the existing implementation / prepare for the future
- documentation of the API and table features
- additional e2e, integration and unit tests for a more mature development platform

Derived Properties
- Derived properties are new to 3.1
- They are readonly properties that represent a transform from multiple 'first-class' properties of the component.
- For example, `derived_viewport_dataframe` is a readonly view based on `(dataframe, filtering params, sorting params, pagination params) --> derived_viewport_dataframe`

Derived properties allow the component to expose complex state that can be useful for a Dash Server developer but without introducing dual states, a situation where multiple properties may represent the same state within the component, making it necessary to reconcile them on each prop update.

Virtual and Viewport Dataframe
- 4 new external facing derived properties and 4 internal facing controlled properties that represent:
    1. the filtered and sorted dataframe and the indices mapping
    2. the filtered, sorted and paginated dataframe and the indices mapping

    - `derived_viewport_dataframe`
    - `derived_viewport_indices`
    - `derived_virtual_dataframe`
    - `derived_virtual_indices`

    In the event where sorting, filtering or pagination is done on the Dash server, it is possible that some or all derived dataframes will be equal to the dataframe prop.

## [3.0.0-rc22]
### Fixed
- Fix regression for user select
    Sorting arrow will no longer highlight.

## [3.0.0-rc21]
### Changed
- Improve performance when the user clicks outside of the table [#104](https://github.com/plotly/dash-table/pull/104)
    Clicking outside of the table was setting the table's `is_focused` property.
    Setting component properties in Dash can be expensive: it can cause the
    entire app to re-render.
    Now, clicking outside the table will update the component more efficiently,
    prevent excessive application re-renders.

## [3.0.0-rc20]
### Fixed
- Fix incorrect border around table cells when not filled [#102](https://github.com/plotly/dash-table/pull/102) [#101](https://github.com/plotly/dash-table/issues/101)
    Table styling has been changed for frozen rows and columns. Default styling change from:

    - frozen rows: { height: 500px } to { height: fit-content, max-height: 500px }
    - frozen columns: { width: 500px } to { width: fit-content, max-width: 500px }

## [3.0.0-rc19]
### Fixed
- Fix dropdown position & behavior on scroll [#96](https://github.com/plotly/dash-table/issues/96)
    Limitation: The dropdown in fixed columns behaves differently from the dropdown in the non-fixed portion of the table. Because of layers of overflow & positioning, the dropdown does not show outside of the table is instead part of it. Opening the dropdown in bottom rows will require scrolling vs. displaying on top of the table.

## [3.0.0-rc18]
### Added
Basic Filtering & Preparation work for advaced filtering
- Additional filtering_type prop that can take value 'basic' (or eventually 'advanced')
    This prop defines whether the user is presented with the UI to filter by column or with complex expressions
    The default value is 'basic'

    Note: The filtering row counts against n_fixed_rows

- Additional filtering_types prop that takes an array of values with valid values 'basic' (and eventually 'advanced')
    This prop defines what type of filtering are available to the user
    The default value is ['basic']

    Note: This value needs to be consistent with `filtering_type`

## [3.0.0-rc17]
### Added
- Make buttons non-selectable [#105](https://github.com/plotly/dash-table/pull/105) [#91](https://github.com/plotly/dash-table/issues/91)

## [3.0.0-rc16]
### Fixed
- Fix keyboard navigation after copy [#90](https://github.com/plotly/dash-table/pull/90) [#49](https://github.com/plotly/dash-table/issues/49)

## [3.0.0-rc15]
### Fixed
- Fix global copy paste regression [#87](https://github.com/plotly/dash-table/pull/87) [#75](https://github.com/plotly/dash-table/issues/75)
- Fix data paste [#87](https://github.com/plotly/dash-table/pull/87) [#88](https://github.com/plotly/dash-table/issues/88)

## [3.0.0-rc14]
### Fixed
- Empty dropdown setting value regression fix [#85](https://github.com/plotly/dash-table/pull/85) [#83](https://github.com/plotly/dash-table/issues/83)

## RC13 - Modify click & sequential click behavior
### Changed
- Partial implementation of new click & sequential click behavior [#79](https://github.com/plotly/dash-table/pull/79) [#77](https://github.com/plotly/dash-table/issues/77)
    - First click selects the cell's content and will cause user input to override the cell content.
    - Second click into the cell will remove the selection and position the cursor accordingly.

## [3.0.0-rc12]
### Fixed
- Fix border style [#78](https://github.com/plotly/dash-table/pull/78) [#68](https://github.com/plotly/dash-table/issues/68)
- Fix selection [#78](https://github.com/plotly/dash-table/pull/78) [#73](https://github.com/plotly/dash-table/issues/73)
- Fix row offset [#78](https://github.com/plotly/dash-table/pull/78) [#76](https://github.com/plotly/dash-table/issues/76)

## [3.0.0-rc11]
### Fixed
- Fix copy/paste regression [#70](https://github.com/plotly/dash-table/pull/70) [#64](https://github.com/plotly/dash-table/issues/64)
- Fix click/blur regression [#70](https://github.com/plotly/dash-table/pull/70) [#65](https://github.com/plotly/dash-table/issues/65)
- Fix delete regression [#70](https://github.com/plotly/dash-table/pull/70) [#67](https://github.com/plotly/dash-table/issues/67)

## [3.0.0-rc10]
### Fixed
- Fix double click regression [#63](https://github.com/plotly/dash-table/pull/63)

## [3.0.0-rc9]
### Added
Treat empty strings as none
- sorting_treat_empty_string_as_none takes value True or False
    Overrides sorting default behavior to consider empty strings as a nully value.
    Note: This is a stopgag prop, full implementation of sorting overrides will most probably deprecate it.
    Default value is False.

## [3.0.0-rc8]
### Fixed
setProps bug fix
- Fixing initialization issue where the FE wrongly believes it's working in DEV mode

## [3.0.0-rc7]
### Added
Additional `sorting_type` prop that can take value 'multi' or 'single'
This prop defines whether the user can sort based on multiple columns or can only sort by one column at a time. The default value is 'single'.

## [3.0.0-rc6]
### Added
Consolidating virtualization, sorting, filtering
- First steps to make sorting work from both FE and BE *
- and consistent with Virtualization settings *

New Props
- sorting -> ['fe', 'be', true, false] (default: false) -- replaces `sortable` prop
- sorting_settings -> array of { field, ascending } -- replaces `sort` prop
- `virtual_dataframe` (READONLY)
- `virtual_dataframe_indices` (READONLY; not officially supported yet -- IN DEVELOPMENT)

virtual_dataframe vs. dataframe
- the virtual dataframe is the content of the viewport for the user (e.g. user has a 10k rows dataframe with FE/250 lines paging, on 1st page -> the `virtual_dataframe` contains items [0,250[ of the dataframe); the dataframe still contains 10k items
- 10k rows, no paging, sorting and filtering -> the virtual dataframe contains items visible in the viewport, in the visible order; the dataframe still contains 10k items
- if the user modifies a cell, the dataframe and the virtual_dataframe are updated with the new data

### Deprecated
- sortable
- sort
- dataframe behavior on sort (see below)

## [3.0.0-rc5]
### Added
New props for Conditional Style, Conditional Dropdown, Filter
- filtering -> ['fe', 'be', true, false] (default: false)
- filtering_settings -> AST query string (default: '')
- column_conditional_dropdowns
- column_static_dropdown
- column_conditional_styles
- column_static_style
- row_conditional_styles
- row_static_style

### Deprecated
- column style
- column options
- dropdown_properties prop

## [3.0.0-rc4]
### Added
Version 3.0 of the Dash-Table expands vastly on the capability of the 2.x table and provides features:
- visually freezing rows and/or columns
- filtering in either FE or BE, basic filtering UI
- sorting in either FE or BE, basic sorting UI
- pagination in either FE or BE, basic pagination UI
- performance optimizations
- basic coverage through e2e, integration and unit tests

Virtualization
- See v_be_page_usage.py and v_fe_page_usage.py for FE and BE usage scenarios.
- virtual_dataframe and virtual_dataframe_indices are exposed and expected to be *readonly*. Setting them from the BE will have no impact on the FE display.
FE Virtualization
- BE is not expected to update the dataframe when the virtualization settings are updated.

BE Virtualization
- BE is expected to update the dataframe when the virtualization settings are updated.

Freeze Top Rows (Limitations)
- the table styling is forced to { table-layout: fixed; width: 0 !important; } to ensure the frozen section and the rest of the table stay in sync (width-wise); this means that the width of the table is only driven by the width of the columns (default width is 200px)
- can't freeze rows and columns at the same time

Freeze Left Columns (Limitations)
- performance is highly impacted if the table is in a scrollable container as the frozen columns position has to be recalculated on each scroll event; impact is minimal up to 50-100 items and makes the table difficult to use with 250-500 items
- can't freeze rows and columns at the same time
- when using merged headers, make sure that the number of fixed columns respects the merged headers, otherwise there will be some unresolved visual bugs/artefacts
- rows are assumed to all have the same height

Deletable Columns (Limitations)
- there might be unintended side-effects if used with BE virtualization (the act of deleting a column / columns modifies the dataframe)

Performance Improvements
- Table now renders and navigates faster
- Typing in cell does not modify dataframe until focus is lost / edit is confirmed ("enter" or "tab)

### Deprecated
- prop "update_on_unfocus" has been removed
