# Change Log for dash-table
### NOTE: as of v2.0, changes in dash-table are all being recorded in the main dash changelog.
### This file is kept only for historical purposes.
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).


## [4.12.0] - 2021-07-09
### Fixed
- [#907](https://github.com/plotly/dash-table/pull/907)
  - Fix a bug where pagination did not work or was not visible. [#834](https://github.com/plotly/dash-table/issues/834)
  - Fix a bug where if you are on a page that no longer exists after the data is updated, no data is displayed. [#892](https://github.com/plotly/dash-table/issues/892)


### Added
- [#916](https://github.com/plotly/dash-table/pull/916)
  - Added `html` option to `markdown_options` prop. This enables the use of html tags in markdown text.

- [#545](https://github.com/plotly/dash-table/issues/545)
    - Case insensitive filtering
    - New props: `filter_options` - to control case of all filters, `columns.filter_options` - to control filter case for each column
    - New operators: `i=`, `ieq`, `i>=`, `ige`, `i>`, `igt`, `i<=`, `ile`, `i<`, `ilt`, `i!=`, `ine`, `icontains` - for case-insensitive filtering, `s=`, `seq`, `s>=`, `sge`, `s>`, `sgt`, `s<=`, `sle`, `s<`, `slt`, `s!=`, `sne`, `scontains` - to force case-sensitive filtering on case-insensitive columns

### Changed
- [#918](https://github.com/plotly/dash-core-components/pull/918) Updated all dependencies. In particular the `highlight.js` upgrade changes code highlighting in markdown: we have long used their "github" style, this has been updated to more closely match current github styles.
- [#901](https://github.com/plotly/dash-core-components/pull/901) Updated R package `dash-info.yaml` to regenerate example without attaching now-deprecated core component packages (`dashHtmlComponents`, `dashCoreComponents`, or `dashTable`).

## [4.11.3] - 2021-04-08
### Changed
- [#862](https://github.com/plotly/dash-table/pull/862) - update docstrings per https://github.com/plotly/dash/issues/1205
- [#878](https://github.com/plotly/dash-table/pull/878) - update build process to use Webpack 5 and other latest dependencies

## [4.11.2] - 2021-01-19
### Fixed
- [#854](https://github.com/plotly/dash-table/pull/854) - part of fixing dash import bug https://github.com/plotly/dash/issues/1143

## [4.11.1] - 2020-12-07
### Fixed
- [#844](https://github.com/plotly/dash-table/pull/844) Fix a bug where the table is using classes that are styled by Bootstrap

## [4.11.0] - 2020-10-29
### Fixed
- [#841](https://github.com/plotly/dash-table/pull/841)
  - Fix prop-types regression causing console errors in browser devtools
  - Fix syntax highlighting regression for Markdown cells
- [#842](https://github.com/plotly/dash-table/pull/842) Fix a regression introduced with [#722](https://github.com/plotly/dash-table/pull/722) causing the tooltips to be misaligned with respect to their parent cell and incompletely addressed in [#817](https://github.com/plotly/dash-table/pull/817)

### Added
- [#841](https://github.com/plotly/dash-table/pull/841) Add Julia syntax highlighting support for Markdown cells
- [#831](https://github.com/plotly/dash-table/pull/831) Add the `tooltip_header` prop and add nested prop `use_with` (with values: `header`, `data`, `both`) to the `tooltip` prop to configure header cell tooltips

## [4.10.1] - 2020-09-03
-Dash.jl Julia component generation

## [4.10.0] - 2020-08-25
### Added
- [#820](https://github.com/plotly/dash-table/pull/820) Add support for Dash.jl Julia built components

### Fixed
- [#817](https://github.com/plotly/dash-table/pull/817) Fix a regression introduced with [#722](https://github.com/plotly/dash-table/pull/722) causing the tooltips to be misaligned with respect to their parent cell
- [#818](https://github.com/plotly/dash-table/pull/818) Fix a regression causing copy/paste not to work when selecting a range of cells with Shift + mouse click
- [#819](https://github.com/plotly/dash-table/pull/819) Fix pagination `page_current` and `page_count` fields to accommodate larger numbers

## [4.9.0] - 2020-07-27
### Added
- [#808](https://github.com/plotly/dash-table/pull/808)Fix a regression introduced with [#787](https://github.com/plotly/dash-table/pull/787) making it impossible to open markdown links in the current tab.
    - Adds a new `markdown_options` property that supports:
        - `link_target` nested prop with values `_blank`, `_parent`, `_self`, `_top` or an arbitrary string (default: `_blank`)

### Fixed
- [#806](https://github.com/plotly/dash-table/pull/806) Fix a bug where fixed rows a misaligned after navigating or editing cells [#803](https://github.com/plotly/dash-table/issues/803)
- [#809](https://github.com/plotly/dash-table/pull/809) Fix a bug where a scrollbar flickers on table render [#801](https://github.com/plotly/dash-table/issues/801)

## [4.8.1] - 2020-06-19
### Fixed
- [#798](https://github.com/plotly/dash-table/pull/798) Fix a bug where headers are not aligned with columns after an update [#797](https://github.com/plotly/dash-table/issues/797)

## [4.8.0] - 2020-06-17
### Added
- [#787](https://github.com/plotly/dash-table/pull/787) Add `cell_selectable` property to allow/disallow cell selection

### Changed
- [#787](https://github.com/plotly/dash-table/pull/787)
    - Clicking on a link in a Markdown cell now requires a single click instead of two
    - Links in Markdown cells now open a new tab (target="_blank")

### Fixed
- [#785](https://github.com/plotly/dash-table/pull/785) Fix a bug where the table does not refresh correctly if a property was previously missing
- [#793](https://github.com/plotly/dash-table/pull/793)
    - Fix a bug where headers are not aligned with columns with fixed_rows [#777](https://github.com/plotly/dash-table/issues/777)
    - Fix a regression where headers don't scroll horizontally with fixed_rows [#780](https://github.com/plotly/dash-table/issues/780)

## [4.7.0] - 2020-05-05
### Added
- [#729](https://github.com/plotly/dash-table/pull/729) Improve conditional styling
    - `style_data_conditional`: Add support for `row_index` and `column_id` array of values
    - `style_header_conditional`: Add support for `header_index` and `column_id` array of values
    - `style_filter_conditional`: Add support for `column_id` array of values
    - `style_cell_conditional`: Add support for `column_id` array of values
    - `style_data_conditional`: Add new conditions `state: 'active'|'selected'` to customize selected and active cell styles

### Fixed
- [#722](https://github.com/plotly/dash-table/pull/722) Fix a bug where row height is misaligned when using fixed_columns and/or fixed_rows
- [#728](https://github.com/plotly/dash-table/pull/728) Fix copy/paste on readonly cells
- [#724](https://github.com/plotly/dash-table/pull/724) Fix `active_cell` docstring: clarify optional nature of the `row_id` nested prop
- [#732](https://github.com/plotly/dash-table/pull/732) Fix a bug where opening a dropdown scrolled the table down its last row
- [#731](https://github.com/plotly/dash-table/pull/731) Fix a bug where `data=None` and `columns=None` caused the table to throw an error
- [#766](https://github.com/plotly/dash-table/pull/766) Sanitize table `id` for stylesheet injection (fixes usage with Pattern-Matching callbacks)

## Changed
- [#758](https://github.com/plotly/dash-table/pull/758) Improve error message for invalid filter queries

## [4.6.2] - 2020-04-01
### Changed
- [#713](https://github.com/plotly/dash-table/pull/713) Update from React 16.8.6 to 16.13.0

## [4.6.1] - 2020-02-27
### Added
- [#711](https://github.com/plotly/dash-table/pull/711) Added R examples to package help

### Changed
- [#704](https://github.com/plotly/dash-table/pull/704) Renamed async modules with hyphen `-` instead of tilde `~`

## [4.6.0] - 2020-01-14
### Added
- [#606](https://github.com/plotly/dash-table/pull/606) Add markdown support for table cells. Cells will be rendered as markdown if the column `presentation` is specified as `markdown`.
    - Add highlight.js for syntax highlighting. If `window.hljs` is specified, that will be used for highlighting instead.

### Fixed
- [#670](https://github.com/plotly/dash-table/pull/670) Fix a bug where `derived_filter_query_structure` was not getting updated properly
- [#677](https://github.com/plotly/dash-table/pull/677) Fix a bug where the table fails to load when used inside an iframe with a sandbox attribute that only has allow-scripts
- [#665](https://github.com/plotly/dash-table/pull/665) Fix a bug in Firefox where the dropdown cells height is incorrect

## [4.5.1] - 2019-11-14
### Fixed
- [#637](https://github.com/plotly/dash-table/pull/637) Fix multiple issues
  - Fix IE11 compatibility issues and add ES5 compatibility and validation
  - Fix a bug with `loading_state` being handled incorrectly, causing the table to steal focus

## [4.5.0] - 2019-10-29
### Changed
- [#554](https://github.com/plotly/dash-table/pull/554) Async loading of `xlsx` library on export

## [4.4.1] - 2019-10-17
### Fixed
- [#618](https://github.com/plotly/dash-table/issues/618) Fix a bug with keyboard navigation not working correctly in certain circumstances when the table contains `readonly` columns.
- [#206](https://github.com/plotly/dash-table/issues/206) Fix a bug with copy/paste to and from column filters not working.
- [#561](https://github.com/plotly/dash-table/issues/561) Fix an incorrect React PureComponent usage causing warnings in DevTools.
- [#611](https://github.com/plotly/dash-table/issues/611) Fix a bug with copy/paste causing hidden columns to be removed from the table

## [4.4.0] - 2019-10-08
### Added
[#546](https://github.com/plotly/dash-table/issues/546)
- New prop `export_columns` that takes values `all` or `visible` (default). This prop controls the columns used during export

[#597](https://github.com/plotly/dash-table/issues/597)
- Add `is blank` unary operator. Returns true for `undefined`, `null` and `''`.

[#299](https://github.com/plotly/dash-table/issues/299)
- New prop `page_count` that sets the maximum number of pages that are
  accessible via the pagination menu when using backend pagination.

### Changed
[#598](https://github.com/plotly/dash-table/issues/598)
- Allow values with whitespaces in column filters

[#580](https://github.com/plotly/dash-table/issues/580)
- Change pagination menu button UI to use arrow icons instead of plain
  buttons
- Move pagination menu to bottom-right of table
- Include go-to-first and go-to-last buttons
- Include current-page and total-pages display in pagination menu
- Include input box for user to navigate directly to a page

### Fixed

[#460](https://github.com/plotly/dash-table/issues/460)
- The `datestartswith` relational operator now supports number comparison
- Fixed a bug where the implicit operator for columns was `equal` instead of the expected default for the column type

[#546](https://github.com/plotly/dash-table/issues/546)
- Visible columns are used correctly for both header and data rows

[#563](https://github.com/plotly/dash-table/issues/563)
- Fixed a bug where any string beginning with a relational operator was being interpreted as that operator being applied to the rest of the string (e.g., "lens" was interpreted as "<=ns")

[#591](https://github.com/plotly/dash-table/issues/591)
- Fixed row and column selection when multiple tables are present

[#600](https://github.com/plotly/dash-table/issues/600)
- Fixed reconciliation when validation default value is `0` (number)
- Apply reconciliation value when deleting cells, if possible

## [4.3.0] - 2019-09-17
### Added
[#566](https://github.com/plotly/dash-table/pull/566)
- Support persisting user edits when the component or the page is reloaded. New props are `persistence`, `persistence_type`, and `persisted_props`. Set `persistence` to a truthy value to enable, the other two modify persistence behavior. See [plotly/dash#903](https://github.com/plotly/dash/pull/903) for more details.

[#319](https://github.com/plotly/dash-table/issues/319)
- New 'loading_state' prop that contains information about which prop, if any, is being computed.
- Table no longer allows for editing while the `data` prop is loading.

### Fixed
[#578](https://github.com/plotly/dash-table/pull/578)
- Fix [#576](https://github.com/plotly/dash-table/issues/576), editing column names or deleting columns while other columns are hidden causing the hidden columns to be lost.
- Fix an unreported bug that clicking "Cancel" at the column name edit prompt would clear the name, rather than leaving it unchanged as it should.

[#569](https://github.com/plotly/dash-table/issues/569), [#544](https://github.com/plotly/dash-table/issues/544)
- Allow empty strings in all `filter_query` (e.g filter_query: '{colA} eq ""')

[#567](https://github.com/plotly/dash-table/issues/567)
- Add support for missing `border-radius` in style_** props
- Fix table's inner vs. outer container styling

[#18](https://github.com/plotly/dash-table/issues/18)
- Fix row selection vertical and horizontal alignment

[#103](https://github.com/plotly/dash-table/issues/103)
- Simplify usage for multi-line cells and ellipsis. The cell's content now inherits the value of
`white-space`, `overflow` and `text-overflow` from its parent, making it possible to style
multi-line & ellipsis with `style_data` and other style props.

[#583](https://github.com/plotly/dash-table/issues/583)
- Fix regression when editing the content of a cell in a scrolled virtualized table

[#539](https://github.com/plotly/dash-table/issues/539)
- Fix bug where boolean values are not showing up in the table

## [4.2.0] - 2019-08-27
### Added
[#317](https://github.com/plotly/dash-table/issues/317)
- New `column.selectable` nested prop that displays a selection checkbox or radio button in the column.
- New `column_selectable` prop to choose whether columns can be selected or not, and whether a single or
    multiple selections can be in effect at the same time.
- New `selected_columns` prop that contains the list of visible and hidden columns that are currently selected
- New `derived_viewport_selected_columns` that contains the list of visible columns that are currently selected
    This prop is read-only. Use `selected_columns` in callbacks instead.

### Fixed
[#533](https://github.com/plotly/dash-table/issues/533)
- Fixed problem clearing one column shifting everything to the left and
leaving the last column blank
- Add merge_duplicate_headers prop to correct `export_format: display` behavior.
[#549](https://github.com/plotly/dash-table/issues/549)
- Fixed renaming of single-row headers in the GUI

## [4.1.0] - 2019-08-05
### Added
[#314](https://github.com/plotly/dash-table/issues/314)
- New `column.hideable` flag that displays an "eye" action icon in the column
    Accepts a boolean, array of booleans, 'last' or 'first'. Clicking on the "eye" will add the column to the `hidden_columns` prop.
    `hidden_columns` can be added back through the Columns toggle menu whether they are hideable or not.
- New accepted values for `column.clearable`, `column.deletable` and `column.renamable`
    These props now also accept 'last' and 'first'.
    - 'last' will display the action only on the last row of the headers
    - 'first' will display the action only on the first row of the headers

[#313](https://github.com/plotly/dash-table/issues/313)
- Ability to export table as csv or xlsx file.

[#497](https://github.com/plotly/dash-table/pull/497)
- New `column.clearable` flag that displays a "eraser" action in the column
    Accepts a boolean or array of booleans for multi-line headers.
    Clicking a merged column's "eraser" will clear all related columns.

    - Clearing column(s) will remove the appropriate data props from each datum
    row of `data`.
    - Additionally clearing the column will reset the filter for the affected column(s)

[#318](https://github.com/plotly/dash-table/issues/318)
- Headers are included when copying from the table to different
tabs and elsewhere. They are ignored when copying from the table onto itself and
between two tables within the same tab.

### Changed
[#497](https://github.com/plotly/dash-table/pull/497)
- Like for clearing above, deleting through the "trash" action will also
reset the filter for the affected column(s)

### Fixed
[#524](https://github.com/plotly/dash-table/issues/524)
- Fixed readonly dropdown cells content (display label, not value)

[#259](https://github.com/plotly/dash-table/issues/259)
- Fixed columns `sticky` on Safari

[#491](https://github.com/plotly/dash-table/issues/491)
- Fixed inconsistent behaviors when editing cell headers

[#521](https://github.com/plotly/dash-table/pull/521)
- Fixed white line artifacts when rendering the table with browser zoom different from 100%

## [4.0.2] - 2019-07-15
### Fixed
[#489](https://github.com/plotly/dash-table/issues/489)
- Add `fill_width` prop to replace `content_style` prop removed in the [4.0 API rework](https://github.com/plotly/dash-table/pull/446)

## [4.0.1] - 2019-07-09
### Changed
[#488](https://github.com/plotly/dash-table/pull/488)
- Update table build for use as a library and make consistent with other Dash repos

## [4.0.0] - 2019-06-20
### Changed
[#446](https://github.com/plotly/dash-table/pull/446)
- Table API rework
#### NEW
    - `column.sort_as_null`: Allows sorting behavior customization.
        Accepts an array of string, number or booleans.

#### REMOVED
    - `column.clearable`: Allows clearing the value of a dropdown cell.
        Removed in favor of `dropdown_**` `clearable` nested property.
    - `column.hidden`: Allows hiding column
        Removed. Stay tuned by following https://github.com/plotly/dash-table/issues/314.
    - `column.options`
        Removed. Redundant with `dropdown`.
    - `content_style`
        Removed. Deemed unnecessary. NOTE - This was added back in 4.0.2 under the name the "fill_width" property name.
    - `pagination_settings`
        Replaced by two props `page_current` and `page_size`.

#### RENAMED
    - `column_static_tooltip`
        Renamed to `tooltip`.
    - `column_conditional_tooltips`
        Renamed to `tooltip_conditional`.
    - `filter`
        Renamed to `filter_query`.
    - `sort_type`
        Renamed to `sort_mode`.
    - `derived_filter_structure`
        Renamed to `derived_filter_query_structure`.

#### MODIFIED
    - `column.deletable`: Allows column deletion.
        Now accepts a boolean or an array of booleans (for multi-line headers).
        For example, if there are multiple headers and you want the second header row to be deletable, this would be `[False, True]`.
    - `column.editable_name`: Allows column renaming.
        Renamed to `column.renamable`
        Now accepts a boolean or an array of booleans (for multi-line headers).
        For example, if there are multiple headers and you want the second row's header's name to be editable, this would be `[False, True]`.
    - `column.id`
        Now accepts `string` only -- `number` column ids can be casted to string.
    - `n_fixed_columns`: Will fix columns to the left.
        Renamed to `fixed_columns`
        Now accepts an object { headers: boolean, data: number } instead of a number.
        { headers: true } determines the number of columns to fix automatically. For example, if the rows are selectable or deletable, { headers: true } would fix those columns automatically. If { headers: true, data: 2 }, it would fix the first two data columns in addition to the selectable and deletable if visible.
    - `n_fixed_rows`: Will fix rows to the top.
        Renamed to `fixed_rows`
        Now accepts an object { headers: boolean, data: number } instead of a number.
        { headers: true } determines the number of rows to fix automatically (i.e. if there are multiple headers, it will fix all of them as well as the filter row).
        { headers: true, data: 2} would fix all of the header rows as well as the first 2 data rows.
    -  `pagination_mode`
        Renamed to `page_action`.
        `'fe'` is now `'native'`, `'be'` is now `'custom'`, and `false` is now '`none'`
    -  `column_static_dropdown`
        Renamed to `dropdown`.
        Now an object with each entry referring to a Column ID. Each nested prop expects.
        `clearable` and `options`.
    - `column_conditional_dropdowns`
        Renamed to `dropdown_conditional`.
        `condition` changed to the same `if` nested prop used by styles.
        `dropdown` renamed to `options`.
    - `dropdown_properties`
        Renamed to `dropdown_data`.
        Matches the `data` structure.
    - `tooltips`
        Renamed to `tooltip_data`.
        Matches the `data` structure.
    - `filtering`
        Renamed to `filter_action`.
    - `sorting`
        Renamed to `sort_action`.
    - `sorting_treat_empty_string_as_none`
        Renamed to `sort_as_null`.
        Now accepts an array of string, number or booleans that can be ignored during sort.
        Table-level prop for the `column.sort_as_null` column nested prop.
    - `style_data_conditional`
        Renamed `filter` to `filter_query`.

### Added
[#320](https://github.com/plotly/dash-table/issues/320)
- Ability to conditionally format columns if editing is disabled.

[#456](https://github.com/plotly/dash-table/issues/456)
- Support for dash-table is now available for R users of Dash.

### Fixed
[#434](https://github.com/plotly/dash-table/issues/434)
- Fix CSS borders properties overwrite style_* borders properties.

[#435](https://github.com/plotly/dash-table/issues/435)
- selected_cells background color is set through styling pipeline / derivations.

## [3.7.0] - 2019-05-15
### Added
[#397](https://github.com/plotly/dash-table/pull/397), [#410](https://github.com/plotly/dash-table/pull/410)
- Improve filtering syntax and capabilities
    - new field syntax `{myField}`
    - short form by-column filter
        - implicit column and default operator based on column type
            - Text and Any columns default to `contains`
            - Numeric columns default to `eq`
            - Date columns default to `datestartswith`
        - implicit column (e.g `ne "value"` becomes `{my-column} ne "value"`)
    - new `contains` relational operator for strings
    - new `datestartswith` relational operator for dates
    - new `eq` behavior (will attempt to convert and compare numeric values if possible)
    - new readonly `derived_filter_structure` prop exposing the query structure in a programmatically friendlier way

[#412](https://github.com/plotly/dash-table/pull/412)
- Add support for row IDs, based on the `'id'` attribute of each row of `data`
    - IDs will not be displayed unless there is a column with `id='id'`
    - `active_cell`, `start_cell`, `end_cell`, and items in `selected_cells` contain row and column IDs: All are now dicts  `{'row', 'column', 'row_id' and 'column_id'}` rather than arrays `[row, column]`.
    - Added new props mirroring all existing row indices props:
        - `selected_row_ids` mirrors `selected_rows`
        - `derived_viewport_row_ids` mirrors `derived_viewport_indices`
        - `derived_virtual_row_ids` mirrors `derived_virtual_indices`
        - `derived_viewport_selected_row_ids` mirrors `derived_viewport_selected_rows`
        - `derived_virtual_selected_row_ids` mirrors `derived_virtual_selected_rows`

[#424](https://github.com/plotly/dash-table/pull/424)
- Customizable cell borders through `style_**` props
    - cell borders now no longer use `box-shadow` and use `border` instead
    - Supports CSS shorthands:
        border, border_bottom, border_left, border_right, border_top
    - style_** props will ignore the following CSS rules:
        border_bottom_color, border_bottom_left_radius, border_bottom_right_radius, border_bottom_style, border_bottom_width, border_collapse, border_color, border_corner_shape, border_image_source, border_image_width, border_left_color, border_left_style, border_left_width, border_right_color, border_right_style, border_right_width, border_spacing, border_style, border_top_color, border_top_left_radius, border_top_right_radius, border_top_style, border_top_width, border_width
    - Styles priority:
        1. Props priority in decreasing order
            style_data_conditional
            style_data
            style_filter_conditional
            style_filter
            style_header_conditional
            style_header
            style_cell_conditional
            style_cell
        2. Within each props, higher index rules win over lower index rules
        3. Previously applied styles of equal priority win over later ones (applied top to bottom, left to right)

### Changed
[#397](https://github.com/plotly/dash-table/pull/397)
- Rename `filtering_settings` to `filter`

[#417](https://github.com/plotly/dash-table/pull/417)
- Rename `sorting_settings` to `sort_by`

[#412](https://github.com/plotly/dash-table/pull/412)
- `active_cell` and `selected_cells` items are dicts `{'row', 'column', 'row_id' and 'column_id'}` instead of arrays `[row, column]`

## [3.6.0] - 2019-03-04
### Fixed
[#189](https://github.com/plotly/dash-table/issues/189)
- Added `format` nested prop to columns
    - Applied to columns with `type=numeric` (more to come)
    - Uses [d3-format](https://github.com/d3/d3-format) under the hood
    - `format.locale` for localization configuration
    - `format.prefix` for SI prefix configuration
    - `format.specifier` for formatting configuration
    - `format.separate_4digits` to configure grouping behavior for numbers with 4 digits or less
    - Python helpers (dash_table.FormatTemplate)
- Added `locale_format` prop to table (default localization configuration, merged with column.format.locale)

[#387](https://github.com/plotly/dash-core/issues/387)
- Fix filtering conditions using floats

## [3.5.0] - 2019-02-25
### Added
[#342](https://github.com/plotly/dash-core/issues/342)
- Added `column_type` condition to style `if`; allows applying styles based on the type of the column for props
    - `style_cell_conditional`
    - `style_data_conditional`
    - `style_filter_conditional`
    - `style_header_conditional`

### Fixed
[#347](https://github.com/plotly/dash-core/issues/347)
- Fixed table behavior when `filtering_settings` is updated through a callback

[#322](https://github.com/plotly/dash-core/issues/322)
- Added LICENSE file to Python distributable

[#342](https://github.com/plotly/dash-core/issues/342)
- Added already supported `filter` nested prop / condition to `style_data_conditional` props definition

## [3.4.0] - 2019-02-08
### Added
[#364](https://github.com/plotly/dash-table/pull/364)
- Added the `datetime` data type

### Changed
[#224](https://github.com/plotly/dash-table/issues/224)
- Added support for unquoted column id with
  - letters, numbers, [-+:.]
- Added support for single and double quoted column id with arbitrary name

### Fixed
[#365](https://github.com/plotly/dash-table/issues/365)
- Incorrect tooltip behavior if cell is in a fixed row or column

- Incorrect default value for `column_static_tooltip` changed from [] to {}

## [3.3.0] - 2019-02-01
### Added
[#307](https://github.com/plotly/dash-core/issues/307)
- Added tooltip_delay and tooltip_duration props to tweak table's tooltips display behavior
- Added tooltips, column_static_tooltip, column_conditional_tooltips to define the tooltip
applicable to a certain cell in the table with nested props delay and duration to override
table's default behavior

## [3.2.0] - 2019-01-25
### Added
[#297](https://github.com/plotly/dash-core/issues/297)
- Added column.validation nested prop to tweak coercion and validation behavior
    - allow_null (boolean): [numeric, text] Allow null/undefined/NaN value
    - default (any): [numeric, text] Default value to use on validation/coercion failure
- Added on user-initiated data change processing (column.on_change.action)
    - Coerce: As Validation + attempts to convert the user-provided value into the destination type
    - None: Accept the user-provided value without verification
    - Validation: Check if the user-provided value is of the correct type/format/etc.
- Added on user-initiated data change failure processing (column.on_change.failure)
    This comes into effect after the column.on_change.action has failed
    - Accept: Accept the user-provide value
    - Default Applies the value defined in column.validation.default
    - Reject: Confirms the failure
### Changed
[#297](https://github.com/plotly/dash-core/issues/297)
- Moved column.type `dropdown` to column.presentation=`dropdown`

## [3.1.12] - 2019-01-11
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
        background_color: 'floralwhite', // from A, not overridden
        color: 'black', // from B, A overridden
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
    - All CSSProperties are supported in kebab-case, camelCase and snake_case

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
- when using merged headers, make sure that the number of fixed columns respects the merged headers, otherwise there will be some unresolved visual bugs/artifacts
- rows are assumed to all have the same height

Deletable Columns (Limitations)
- there might be unintended side-effects if used with BE virtualization (the act of deleting a column / columns modifies the dataframe)

Performance Improvements
- Table now renders and navigates faster
- Typing in cell does not modify dataframe until focus is lost / edit is confirmed ("enter" or "tab)

### Deprecated
- prop "update_on_unfocus" has been removed
