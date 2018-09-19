# Changelog

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