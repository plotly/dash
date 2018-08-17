# Dash Spreadsheet

## Virtualization
    See v_be_page_usage.py and v_fe_page_usage.py for FE and BE usage scenarios.

    virtual_dataframe and virtual_dataframe_indices are exposed and expected to be *readonly*. Setting them from the BE will have no impact on the FE display.

### FE Virtualization
    BE is not expected to update the dataframe when the virtualization settings are updated.

### BE Virtualization
    BE is expected to update the dataframe when the virtualization settings are updated.

## Freeze Top Rows
    Limitations
        - the table styling is forced to { table-layout: fixed; width: 0 !important; } to ensure the frozen section and the rest of the table stay in sync (width-wise); this means that the width of the table is only driven by the width of the columns (default width is 200px)
        - can't freeze rows and columns at the same time

## Freeze Left Columns
    Limitations
        - performance is highly impacted if the table is in a scrollable container as the frozen columns position has to be recalculated on each scroll event; impact is minimal up to 50-100 items and makes the table difficult to use with 250-500 items
        - can't freeze rows and columns at the same time
        - when using merged headers, make sure that the number of fixed columns respects the merged headers, otherwise there will be some unresolved visual bugs/artefacts
        - rows are assumed to all have the same height

## Deletable Columns
    Limitations
        - there might be unintended side-effects if used with BE virtualization (the act of deleting a column / columns modifies the dataframe)