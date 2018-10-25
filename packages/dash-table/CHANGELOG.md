# Changelog

# Version 3.0 (ALPHA)

Version 3.0 of the Dash-Table expands vastly on the capability of the 2.x table and provides features:

    - visually freezing rows and/or columns
    - filtering in either FE or BE, basic filtering UI
    - sorting in either FE or BE, basic sorting UI
    - pagination in either FE or BE, basic pagination UI
    - performance optimizations
    - basic coverage through e2e, integration and unit tests

## RC1, RC2, RC3, RC4 (Virtualization, Freeze, Deletable & Editable Columns, Performance)

### Virtualization

    See v_be_page_usage.py and v_fe_page_usage.py for FE and BE usage scenarios.

    virtual_dataframe and virtual_dataframe_indices are exposed and expected to be *readonly*. Setting them from the BE will have no impact on the FE display.

#### FE Virtualization

    BE is not expected to update the dataframe when the virtualization settings are updated.

#### BE Virtualization

    BE is expected to update the dataframe when the virtualization settings are updated.

### Freeze Top Rows

    Limitations
        - the table styling is forced to { table-layout: fixed; width: 0 !important; } to ensure the frozen section and the rest of the table stay in sync (width-wise); this means that the width of the table is only driven by the width of the columns (default width is 200px)
        - can't freeze rows and columns at the same time

### Freeze Left Columns

    Limitations
        - performance is highly impacted if the table is in a scrollable container as the frozen columns position has to be recalculated on each scroll event; impact is minimal up to 50-100 items and makes the table difficult to use with 250-500 items
        - can't freeze rows and columns at the same time
        - when using merged headers, make sure that the number of fixed columns respects the merged headers, otherwise there will be some unresolved visual bugs/artefacts
        - rows are assumed to all have the same height

### Deletable Columns

    Limitations
        - there might be unintended side-effects if used with BE virtualization (the act of deleting a column / columns modifies the dataframe)

### Performance Improvements

    - Table now renders and navigates faster
    - Typing in cell does not modify dataframe until focus is lost / edit is confirmed ("enter" or "tab)

    Deprecated
        - prop "update_on_unfocus" has been removed

## RC5 (Conditional Style, Conditional Dropdown, Filter)

    New props
        - filtering -> ['fe', 'be', true, false] (default: false)
        - filtering_settings -> AST query string (default: '')
        - column_conditional_dropdowns
        - column_static_dropdown
        - column_conditional_styles
        - column_static_style
        - row_conditional_styles
        - row_static_style
    Deprecated
        - column style
        - column options
        - dropdown_properties

## RC6 - Consolidating virtualization, sorting, filtering

    * First steps to make sorting work from both FE and BE *
    * and consistent with Virtualization settings *

    New Props
        - sorting -> ['fe', 'be', true, false] (default: false) -- replaces 'sortable' prop
        - sorting_settings -> array of { field, ascending } -- replaces 'sort' prop
        - virtual_dataframe (READONLY)
        - virtual_dataframe_indices (READONLY; not officially supported yet -- IN DEVELOPMENT)
    Deprecated
        - sortable
        - sort
        - dataframe behavior on sort (see below)

    virtual_dataframe vs. dataframe
        - the virtual dataframe is the content of the viewport for the user (e.g. user has a 10k rows dataframe with FE/250 lines paging, on 1st page -> the virtual_dataframe contains items [0,250[ of the dataframe); the dataframe still contains 10k items
        - 10k rows, no paging, sorting and filtering -> the virtual dataframe contains items visible in the viewport, in the visible order; the dataframe still contains 10k items
        - if the user modifies a cell, the dataframe and the virtual_dataframe are updated with the new data

## RC7 - Sorting props

    - Additional sorting_type prop that can take value 'multi' or 'single'
        This prop defines whether the user can sort based on multiple columns or can only sort by one column at a time. The default value is 'single'.

## RC8 - setProps bug fix

    - Fixing initialization issue where the FE wrongly believes it's working in DEV mode

## RC9 - Treat empty strings as none

    - sorting_treat_empty_string_as_none takes value True or False

        Overrides sorting default behavior to consider empty strings as a nully value.

        Note: This is a stopgag prop, full implementation of sorting overrides will most probably deprecate it.

        Default value is False.

## RC10 - Fix double click regression

    Issue: https://github.com/plotly/dash-table/issues/62

## RC11 - Fix copy/paste regression, fix delete regression, fix click/blur regression

    Issue: https://github.com/plotly/dash-table/issues/64
    Issue: https://github.com/plotly/dash-table/issues/65
    Issue: https://github.com/plotly/dash-table/issues/67

## RC12 - Dropdown regression fix, border style fix, zoom/resize fix

    Issue: https://github.com/plotly/dash-table/issues/68
    Issue: https://github.com/plotly/dash-table/issues/73
    Issue: https://github.com/plotly/dash-table/issues/76

## RC13 - Modify click & sequential click behavior

    Incremental improvement for:
    Issue: https://github.com/plotly/dash-table/issues/77

    First click selects the cell's content and will cause user input to override the cell content.
    Second click into the cell will remove the selection and position the cursor accordingly.

## RC14 - Empty dropdown setting value regression fix

    Issue: https://github.com/plotly/dash-table/issues/83

## RC15 - Global copy/paste (through browser menu), incorrect pasted data fix

    Issue: https://github.com/plotly/dash-table/issues/75
    Issue: https://github.com/plotly/dash-table/issues/88

## RC16 - Fix incorrect keyboard navigation

    Issue: https://github.com/plotly/dash-table/issues/49

## RC17 - UX Improvements

    Issue: https://github.com/plotly/dash-table/issues/91

    - Navigation and selection UX fine tuning

## RC18 - Filtering (Basic) & Preparation work advanced filtering

    - Additional filtering_type prop that can take value 'basic' (or eventually 'advanced')
        This prop defines whether the user is presented with the UI to filter by column or with complex expressions

        The default value is 'basic'

        Note: The filtering row counts against n_fixed_rows

    - Additional filtering_types prop that takes an array of values with valid values 'basic' (and eventually 'advanced')
        This prop defines what type of filtering are available to the user

        The default value is ['basic']

        Note: This value needs to be consistent with filtering_type

## RC19 - Fix dropdown position & behavior on scroll

    Issue: https://github.com/plotly/dash-table/issues/96

    Limitation: The dropdown in fixed columns behaves differently from the dropdown in the non-fixed portion of the table. Because of layers of overflow & positioning, the dropdown does not show outside of the table is instead part of it. Opening the dropdown in bottom rows will require scrolling vs. displaying on top of the table.

## RC20 - Fix incorrect border around table cells when not filled

    Issue: https://github.com/plotly/dash-table/issues/101

    Table styling has been changed for frozen rows and columns. Default styling change from:

    - frozen rows: { height: 500px } to { height: fit-content, max-height: 500px }
    - frozen columns: { width: 500px } to { width: fit-content, max-width: 500px }

## RC21 - Improve performance when the user clicks outside of the table

    Pull Request: https://github.com/plotly/dash-table/pull/104

    Clicking outside of the table was setting the table's `is_focused` property.
    Setting component properties in Dash can be expensive: it can cause the
    entire app to re-render.
    Now, clicking outside the table will update the component more efficiently,
    prevent excessive application re-renders.

## RC22 - Fix regression for user select

    Regression from: https://github.com/plotly/dash-table/pull/93
    Issue: https://github.com/plotly/dash-table/issues/91

    Sorting arrow will no longer highlight.

# Version 3.1 (BETA)

Version 3.1 of the Dash-Table builds upon the 3.0 table and solidifies the external facing API of the table

    - introducing the notion of derived properties

    - virtual and viewport dataframe and indices for more flexibility
    - code refactoring to simplify and improve the existing implementation / prepare for the future
    - documentation of the API and table features
    - additional e2e, integration and unit tests for a more mature development platform

### Derived Properties

Derived properties are new to 3.1
They are readonly properties that represent a transform from multiple 'first-class' properties of the component.

For example, derived_viewport_dataframe is a readonly view based on
    f(dataframe, filtering params, sorting params, pagination params) --> derived_viewport_dataframe

Derived properties allow the component to expose complex state that can be useful for a Dash Server developer but without introducing dual states, a situation where multiple properties may represent the same state within the component, making it necessary to reconcile them on each prop update.

## RC1 - Virtual and Viewport Dataframe

    - 4 new external facing derived properties and 4 internal facing controlled properties that represent:
        1. the filtered and sorted dataframe and the indices mapping
        2. the filtered, sorted and paginated dataframe and the indices mapping

        - derived_viewport_dataframe
        - derived_viewport_indices
        - derived_virtual_dataframe
        - derived_virtual_indices

        In the event where sorting, filtering or pagination is done on the Dash Server, it is possible that some or all derived dataframes will be equal to the dataframe prop.

## RC2 - Clean up column offsets

    - 1 new internal facing derived/controlled property:
        columns: Columns -> columns: VisibleColumns
        Gets rid of conditional processing for hidden columns in the cell and header factories as well as in navigation/selection handlers

    - A bunch of offsets were introduced to the table in the previous development cycle (2.x -> 3.0). Turns out these offsets are neither useful or necessary
    - Validate compatibility of filtering, sorting, pagination
    - External facing classes and attributes
        * (ATTRIBUTE) data-dash-column=<columnId>

            .dash-cell,
            .dash-header {
                &[data-dash-column='ticker'] {
                    // styling
                }
            }

        * (CLASS) dash-cell
        * (CLASS) dash-header

        * (CLASS) dash-delete-cell
        * (CLASS) dash-delete-header
        * (CLASS) dash-select-cell
        * (CLASS) dash-select-header

        * (CLASS) dash-cell-value

        * (CLASS) dash-freeze-left
        * (CLASS) dash-freeze-top
        * (CLASS) dash-spreadsheet
        * (CLASS) dash-spreadsheet-container
        * (CLASS) dash-spreadsheet-inner

## RC3 - Miscellaneous fixes for pagination, virtual df and viewport df

    Issue: https://github.com/plotly/dash-table/pull/112

## RC4 - Columns width percentage and default (fit to content) support

    * Added prop content_style that takes values 'fit' or 'grow' (Default='fit')
    * Added width percentage support
    * Modified default column behavior from fixed width to 'fit content'
    * Modified width, min-width, max-width interaction on columns

### Width percentage

    Columns can now accept '%' width, minWidth, maxWidth

    For the percentages to have meaning, the dash-table must be forced to have a width and the content of the dash-table must be forced to grow to fill the available space made available by the container (by default the table is only as big as it needs to be).

    To use percentage-based column widths, add:

    * content style
        content_style='grow'

    * table style (example)
        table_style=[{ selector: '.dash-spreadsheet', rule: 'width: 100%; max-width: 100%' }]

    * column with %-based width
        columns=[{
            id: 'column',
            width: '40%'
        }]

### Default column width

    Columns now default to 'fit to content' when no width is defined

    Note: If pagination is used or the dataframe modified, the column width will be re-evaluated on each modification.

### Interaction between width, min-width and max-width

    Column min-width and max-width do not default to width value is not defined.

## RC5 - Tests and fixes for editable/readonly

    Issue: https://github.com/plotly/dash-table/issues/132

## RC6 - Styling API refactoring

    * Remove column width / maxWidth / minWidth
    * Rename property table_style to css

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

    * Add new property style_table of form
        { ...CSSProperties }
    * Add new property style_cell of form
        { ...CSSProperties }
    * Add new property style_data of form
        { ...CSSProperties }
    * Add new property style_filter of form
        { ...CSSProperties }
    * Add new property style_header of form
        { ...CSSProperties }
    * Add new property style_cell_conditional of form
        [{
            if: { column_id: string | number },
            ...CSSProperties
        }]
    * Add new property style_data_conditional of form
        [{
            if: { column_id: string | number, filter: string, row_index: number | 'odd' | 'even' },
            ...CSSProperties
        }]
    * Add new property style_filter_conditional of form
        [{
            if: { column_id: string | number },
            ...CSSProperties
        }]
    * Add new property style_header_conditional of form
        [{
            if: { column_id: string | number, header_index: number | 'odd' | 'even' },
            ...CSSProperties
        }]
    * All CSSProperties are supported in kebab-cass, camelCase and snake_case

    * Renaming 'dataframe' props to 'data'

        dataframe -> data
        dataframe_previous -> data_previous
        dataframe_timestamp -> data_timestamp
        derived_virtual_dataframe -> derived_virtual_data
        derived_viewport_datafram -> derived_viewport_data

## RC7 - Optional id prop

    - The id prop of the table is now optional. It will generate a random id if it's not set.
    Issue: https://github.com/plotly/dash-table/issues/143

## RC8 - Improve props typing

    Issue: https://github.com/plotly/dash-table/issues/143    

## RC9 - Sort ascending on first click

    - Sorts ascending when first clicked, [#118](https://github.com/plotly/dash-table/issues/118)
    - Flips icons displayed so that they are pointing up on ascending and down on descending.
    Issue: https://github.com/plotly/dash-table/issues/143

## RC10 - Improved props docstrings

    Issue: https://github.com/plotly/dash-table/issues/163
    
## RC11 - Style as list view

    - Fix regressions linked to the style_as_list_view feature / prop
