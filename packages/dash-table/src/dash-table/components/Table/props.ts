import { SortSettings } from 'core/sorting';
import { IPaginator } from 'dash-table/derived/paginator';
import {
    Table,
    BasicFilters,
    Cells,
    DataCells,
    Headers,
    Style
} from 'dash-table/derived/style/props';
import {
    ConditionalTooltip,
    Tooltip
} from 'dash-table/tooltips/props';

export enum ColumnType {
    Any = 'any',
    Numeric = 'numeric',
    Text = 'text',
    Datetime = 'datetime'
}

export enum FilteringType {
    Advanced = 'advanced',
    Basic = 'basic'
}

export interface IDerivedData {
    data: Data;
    indices: Indices;
}

export interface IViewportOffset {
    rows: number;
    columns: number;
}

export interface IViewportPadding {
    before: number;
    after: number;
}

export interface IVirtualizedDerivedData extends IDerivedData {
    offset: IViewportOffset;
    padding: {
        rows: IViewportPadding;
    };
}

export enum ContentStyle {
    Fit = 'fit',
    Grow = 'grow'
}

export interface ICellCoordinates {
    row: number;
    column: number;
    row_id?: RowId;
    column_id: ColumnId;
}

export type ColumnId = string | number;
export type Columns = IColumn[];
export type Data = Datum[];
export type Datum =  IDatumObject | any;
export type Filtering = 'fe' | 'be' | boolean;
export type Indices = number[];
export type RowId = string | number;
export type Navigation = 'page';
export type PaginationMode = 'fe' | 'be' | boolean;
export type RowSelection = 'single' | 'multi' | false;
export type SelectedCells = ICellCoordinates[];
export type SetProps = (...args: any[]) => void;
export type SetState = (state: Partial<IState>) => void;
export type Sorting = 'fe' | 'be' | boolean;
export type SortingType = 'multi' | 'single';
export type VisibleColumns = IVisibleColumn[];

export enum ChangeAction {
    Coerce = 'coerce',
    None = 'none',
    Validate = 'validate'
}

export enum ChangeFailure {
    Default = 'default',
    Accept = 'accept',
    Reject = 'reject'
}

export enum Presentation {
    Dropdown = 'dropdown',
    Input = 'input'
}

export interface IChangeOptions {
    action?: ChangeAction;
    failure?: ChangeFailure;
}

export interface IAnyColumn {
    on_change?: undefined;
    presentation?: Presentation.Input | Presentation.Dropdown;
    type?: ColumnType.Any;
    validation?: undefined;
}

export interface ITypeValidation {
    allow_null?: boolean;
    default?: null | number;
}

export interface ITypeColumn {
    on_change?: IChangeOptions;
    validation?: ITypeValidation;
}

export interface INumberLocale {
    symbol: [string, string];
    decimal: string;
    group: string;
    grouping: number[];
    numerals?: string[];
    percent: string;
    separate_4digits?: boolean;
}

export type NumberFormat = ({
    locale: INumberLocale;
    nully: any;
    prefix?: number;
    specifier: string;
}) | undefined;

export interface INumberColumn extends ITypeColumn {
    format?: NumberFormat;
    presentation?: Presentation.Input | Presentation.Dropdown;
    type: ColumnType.Numeric;
}

export interface ITextColumn extends ITypeColumn {
    presentation?: Presentation.Input | Presentation.Dropdown;
    type: ColumnType.Text;
}

export interface IDateValidation extends ITypeValidation {
    allow_YY?: boolean;
}

export interface IDatetimeColumn extends ITypeColumn {
    presentation?: Presentation.Input | Presentation.Dropdown;
    type: ColumnType.Datetime;
    validation?: IDateValidation;
}

export interface IBaseVisibleColumn {
    clearable?: boolean;
    deletable?: boolean | number;
    editable?: boolean;
    editable_name?: boolean | number;
    id: ColumnId;
    name: string | string[];
    options?: IDropdownValue[]; // legacy
}

export type IColumnType = INumberColumn | ITextColumn | IDatetimeColumn | IAnyColumn;
export type IVisibleColumn = IBaseVisibleColumn & IColumnType;

export type IColumn = IVisibleColumn & {
    hidden?: boolean;
};

interface IDatumObject {
    [key: string]: any;
}

export interface IDropdownValue {
    label: string;
    value: string | number;
}

export type DropdownValues = IDropdownValue[];

interface IConditionalDropdown {
    condition: string;
    dropdown: IDropdownValue[];
}

export  interface IColumnDropdown {
    id: string;
    dropdown: IDropdownValue[];
}

export interface IConditionalColumnDropdown {
    id: string;
    dropdowns: IConditionalDropdown[];
}

export interface IDropdownProperties {
    [key: string]: { options: IDropdownValue[] }[];
}

export interface ITableTooltips {
    [key: string]: Tooltip[];
}

export interface ITableStaticTooltips {
    [key: string]: Tooltip;
}

interface IStylesheetRule {
    selector: string;
    rule: string;
}

export interface IPaginationSettings {
    current_page: number;
    page_size: number;
}

export interface IUserInterfaceCell {
    height: number;
}

export interface IUserInterfaceViewport {
    scrollLeft: number;
    scrollTop: number;
    height: number;
    width: number;
}

export interface IUSerInterfaceTooltip {
    delay?: number;
    duration?: number;
    id: ColumnId;
    row: number;
}

export interface IState {
    forcedResizeOnly: boolean;
    rawFilterQuery: string;
    scrollbarWidth: number;
    tooltip?: IUSerInterfaceTooltip;
    uiViewport?: IUserInterfaceViewport;
    uiCell?: IUserInterfaceCell;
    uiHeaders?: IUserInterfaceCell[];
}

export type StandaloneState = IState & Partial<PropsWithDefaultsAndDerived>;

export interface IProps {
    data_previous?: any[];
    data_timestamp?: number;
    end_cell?: ICellCoordinates;
    is_focused?: boolean;
    start_cell?: ICellCoordinates;

    id: string;

    tooltips?: ITableTooltips;
    tooltip_delay: number | null;
    tooltip_duration: number | null;
    column_static_tooltip: ITableStaticTooltips;
    column_conditional_tooltips: ConditionalTooltip[];

    active_cell?: ICellCoordinates;
    columns?: Columns;
    column_conditional_dropdowns?: IConditionalColumnDropdown[];
    column_static_dropdown?: IColumnDropdown[];
    content_style: ContentStyle;
    css?: IStylesheetRule[];
    data?: Data;
    dropdown_properties: any; // legacy
    editable?: boolean;
    filter?: string;
    filtering?: Filtering;
    filtering_type?: FilteringType;
    filtering_types?: FilteringType[];
    locale_format: INumberLocale;
    merge_duplicate_headers?: boolean;
    navigation?: Navigation;
    n_fixed_columns?: number;
    n_fixed_rows?: number;
    row_deletable?: boolean;
    row_selectable?: RowSelection;
    selected_cells?: SelectedCells;
    selected_rows?: Indices;
    selected_row_ids?: RowId[];
    setProps?: SetProps;
    sorting?: Sorting;
    sort_by?: SortSettings;
    sorting_type?: SortingType;
    sorting_treat_empty_string_as_none?: boolean;
    style_as_list_view?: boolean;
    pagination_mode?: PaginationMode;
    pagination_settings?: IPaginationSettings;

    style_data?: Style;
    style_cell?: Style;
    style_filter?: Style;
    style_header?: Style;

    style_data_conditional?: DataCells;
    style_cell_conditional?: Cells;
    style_filter_conditional?: BasicFilters;
    style_header_conditional?: Headers;
    style_table?: Table;
    virtualization?: boolean;
}

interface IDefaultProps {
    active_cell: ICellCoordinates;
    columns: Columns;
    column_conditional_dropdowns: IConditionalColumnDropdown[];
    column_static_dropdown: IColumnDropdown[];
    css: IStylesheetRule[];
    data: Data;
    editable: boolean;
    filter: string;
    filtering: Filtering;
    filtering_type: FilteringType;
    filtering_types: FilteringType[];
    merge_duplicate_headers: boolean;
    navigation: Navigation;
    n_fixed_columns: number;
    n_fixed_rows: number;
    row_deletable: boolean;
    row_selectable: RowSelection;
    selected_cells: SelectedCells;
    start_cell: ICellCoordinates;
    end_cell: ICellCoordinates;
    selected_rows: Indices;
    selected_row_ids: RowId[];
    sorting: Sorting;
    sort_by: SortSettings;
    sorting_type: SortingType;
    sorting_treat_empty_string_as_none: boolean;
    style_as_list_view: boolean;

    pagination_mode: PaginationMode;
    pagination_settings: IPaginationSettings;

    style_data: Style;
    style_cell: Style;
    style_filter: Style;
    style_header: Style;

    style_data_conditional: DataCells;
    style_cell_conditional: Cells;
    style_filter_conditional: BasicFilters;
    style_header_conditional: Headers;

    style_table: Table;
    virtualization: boolean;
}

interface IDerivedProps {
    derived_filter_structure: object | null;
    derived_viewport_data: Data;
    derived_viewport_indices: Indices;
    derived_viewport_row_ids: RowId[];
    derived_viewport_selected_rows: Indices;
    derived_viewport_selected_row_ids: RowId[];
    derived_virtual_data: Data;
    derived_virtual_indices: Indices;
    derived_virtual_row_ids: RowId[];
    derived_virtual_selected_rows: Indices;
    derived_virtual_selected_row_ids: RowId[];
}

export type PropsWithDefaults = IProps & IDefaultProps;
export type PropsWithDefaultsAndDerived = PropsWithDefaults & IDerivedProps;

export type ControlledTableProps = PropsWithDefaults & IState & {
    setProps: SetProps;
    setState: SetState;

    columns: VisibleColumns;
    paginator: IPaginator;
    tooltip: IUSerInterfaceTooltip;
    viewport: IDerivedData;
    viewport_selected_rows: Indices;
    virtual: IDerivedData;
    virtual_selected_rows: Indices;
    virtualized: IVirtualizedDerivedData;
};

export interface ICellFactoryProps {
    active_cell: ICellCoordinates;
    columns: VisibleColumns;
    column_conditional_dropdowns: IConditionalColumnDropdown[];
    column_conditional_tooltips: ConditionalTooltip[];
    column_static_dropdown: IColumnDropdown[];
    column_static_tooltip: ITableStaticTooltips;
    data: Data;
    dropdown_properties: any; // legacy
    editable: boolean;
    id: string;
    is_focused?: boolean;
    n_fixed_columns: number;
    n_fixed_rows: number;
    paginator: IPaginator;
    row_deletable: boolean;
    row_selectable: RowSelection;
    selected_cells: SelectedCells;
    start_cell: ICellCoordinates;
    end_cell: ICellCoordinates;
    selected_rows: Indices;
    setProps: SetProps;
    setState: SetState;
    style_cell: Style;
    style_data: Style;
    style_filter: Style;
    style_header: Style;
    style_cell_conditional: Cells;
    style_data_conditional: DataCells;
    style_filter_conditional: BasicFilters;
    style_header_conditional: Headers;
    style_table: Table;
    tooltip: IUSerInterfaceTooltip;
    tooltips?: ITableTooltips;
    uiCell?: IUserInterfaceCell;
    uiViewport?: IUserInterfaceViewport;
    viewport: IDerivedData;
    virtualization: boolean;
    virtualized: IVirtualizedDerivedData;
}
