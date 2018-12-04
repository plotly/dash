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

export enum ColumnType {
    Dropdown = 'dropdown',
    Numeric = 'numeric',
    Text = 'text'
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

export type ActiveCell = CellCoordinates | [];
export type CellCoordinates = [number, number];
export type ColumnId = string | number;
export type Columns = IColumn[];
export type Data = Datum[];
export type Datum =  IDatumObject | any;
export type Filtering = 'fe' | 'be' | boolean;
export type Indices = number[];
export type Navigation = 'page';
export type PaginationMode = 'fe' | 'be' | boolean;
export type RowSelection = 'single' | 'multi' | false;
export type SelectedCells = CellCoordinates[];
export type SetProps = (...args: any[]) => void;
export type SetState = (state: Partial<IState>) => void;
export type Sorting = 'fe' | 'be' | boolean;
export type SortingType = 'multi' | 'single';
export type VisibleColumns = IVisibleColumn[];

export interface IColumn extends IVisibleColumn {
    hidden?: boolean;
}

export interface IVisibleColumn {
    clearable?: boolean;
    deletable?: boolean | number;
    editable?: boolean;
    editable_name?: boolean | number;
    id: ColumnId;
    name: string | string[];
    options?: { label: string | number, value: string | number }[]; // legacy
    type?: ColumnType;
}

interface IDatumObject {
    [key: string]: any;
}

interface IDropdownValue {
    label: string;
    value: string | number;
}

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

interface IStylesheetRule {
    selector: string;
    rule: string;
}

export interface IPaginationSettings {
    displayed_pages: number;
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

export interface IState {
    forcedResizeOnly: boolean;
    scrollbarWidth: number;
    uiViewport?: IUserInterfaceViewport;
    uiCell?: IUserInterfaceCell;
    uiHeaders?: IUserInterfaceCell[];
}

export type StandaloneState = IState & Partial<PropsWithDefaultsAndDerived>;

interface IProps {
    data_previous?: any[];
    data_timestamp?: number;
    end_cell?: [number, number];
    is_focused?: boolean;
    start_cell?: [number, number];

    id: string;

    active_cell?: ActiveCell;
    columns?: Columns;
    column_conditional_dropdowns?: IConditionalColumnDropdown[];
    column_static_dropdown?: IColumnDropdown[];
    content_style: ContentStyle;
    css?: IStylesheetRule[];
    data?: Data;
    dropdown_properties: any; // legacy
    editable?: boolean;
    filtering?: Filtering;
    filtering_settings?: string;
    filtering_type?: FilteringType;
    filtering_types?: FilteringType[];
    merge_duplicate_headers?: boolean;
    navigation?: Navigation;
    n_fixed_columns?: number;
    n_fixed_rows?: number;
    row_deletable?: boolean;
    row_selectable?: RowSelection;
    selected_cells?: SelectedCells;
    selected_rows?: Indices;
    setProps?: SetProps;
    sorting?: Sorting;
    sorting_settings?: SortSettings;
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
    active_cell: ActiveCell;
    columns: Columns;
    column_conditional_dropdowns: IConditionalColumnDropdown[];
    column_static_dropdown: IColumnDropdown[];
    css: IStylesheetRule[];
    data: Data;
    editable: boolean;
    filtering: Filtering;
    filtering_settings: string;
    filtering_type: FilteringType;
    filtering_types: FilteringType[];
    merge_duplicate_headers: boolean;
    navigation: Navigation;
    n_fixed_columns: number;
    n_fixed_rows: number;
    row_deletable: boolean;
    row_selectable: RowSelection;
    selected_cells: SelectedCells;
    selected_rows: number[];
    sorting: Sorting;
    sorting_settings: SortSettings;
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
    derived_viewport_data: Data;
    derived_viewport_indices: Indices;
    derived_viewport_selected_rows: Indices;
    derived_virtual_data: Data;
    derived_virtual_indices: Indices;
    derived_virtual_selected_rows: Indices;
}

export type PropsWithDefaults = IProps & IDefaultProps;
export type PropsWithDefaultsAndDerived = PropsWithDefaults & IDerivedProps;

export type ControlledTableProps = PropsWithDefaults & IState & {
    setProps: SetProps;
    setState: SetState;

    columns: VisibleColumns;
    paginator: IPaginator;
    viewport: IDerivedData;
    viewport_selected_rows: Indices;
    virtual: IDerivedData;
    virtual_selected_rows: Indices;
    virtualized: IVirtualizedDerivedData;
};

export interface ICellFactoryProps {
    active_cell: ActiveCell;
    columns: VisibleColumns;
    column_conditional_dropdowns: IConditionalColumnDropdown[];
    column_static_dropdown: IColumnDropdown[];
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
    selected_rows: number[];
    setProps: SetProps;
    style_cell: Style;
    style_data: Style;
    style_filter: Style;
    style_header: Style;
    style_cell_conditional: Cells;
    style_data_conditional: DataCells;
    style_filter_conditional: BasicFilters;
    style_header_conditional: Headers;
    style_table: Table;
    uiCell?: IUserInterfaceCell;
    uiViewport?: IUserInterfaceViewport;
    viewport: IDerivedData;
    virtualization: boolean;
    virtualized: IVirtualizedDerivedData;
}