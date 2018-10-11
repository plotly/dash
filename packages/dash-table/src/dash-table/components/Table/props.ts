import { SortSettings } from 'core/sorting';
import { IPaginator } from 'dash-table/derived/paginator';

export enum ColumnType {
    Dropdown = 'dropdown',
    Numeric = 'numeric',
    Text = 'text'
}

export enum FilteringType {
    Advanced = 'advanced',
    Basic = 'basic'
}

export interface IDerivedDataframe {
    dataframe: Dataframe;
    indices: Indices;
}

export enum ContentStyle {
    Fit = 'fit',
    Grow = 'grow'
}

export type ActiveCell = CellCoordinates | [];
export type CellCoordinates = [number, number];
export type ColumnId = string | number;
export type Columns = IColumn[];
export type Dataframe = Datum[];
export type Datum =  IDatumObject | any;
export type Filtering = 'fe' | 'be' | boolean;
export type Indices = number[];
export type Navigation = 'page';
export type PaginationMode = 'fe' | 'be' | boolean;
export type RowSelection = 'single' | 'multi' | false;
export type SelectedCells = CellCoordinates[];
export type SetProps = (...args: any[]) => void;
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
    name: string;
    options?: { label: string | number, value: any }[]; // legacy
    maxWidth?: string | number;
    minWidth?: string | number;
    type?: ColumnType;
    width?: string | number;
}

interface IDatumObject {
    [key: string]: any;
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

interface IProps {
    dataframe_previous?: any[];
    dataframe_timestamp?: number;
    end_cell?: [number, number];
    is_focused?: boolean;
    start_cell?: [number, number];

    id: string;

    active_cell?: ActiveCell;
    columns?: Columns;
    column_conditional_dropdowns?: any[];
    column_conditional_styles?: any[];
    column_static_dropdown?: any;
    column_static_style?: any;
    content_style: ContentStyle;
    dataframe?: Dataframe;
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
    row_conditional_styles?: any[];
    row_deletable?: boolean;
    row_selectable?: RowSelection;
    row_static_style?: any;
    selected_cell?: SelectedCells;
    selected_rows?: number[];
    setProps?: SetProps;
    sorting?: Sorting;
    sorting_settings?: SortSettings;
    sorting_type?: SortingType;
    table_style?: IStylesheetRule[];
    sorting_treat_empty_string_as_none?: boolean;
    pagination_mode?: PaginationMode;
    pagination_settings?: IPaginationSettings;
}

interface IDefaultProps {
    active_cell: ActiveCell;
    columns: Columns;
    column_conditional_dropdowns: any[];
    column_conditional_styles: any[];
    column_static_dropdown: any;
    column_static_style: any;
    dataframe: Dataframe;
    editable: boolean;
    filtering: Filtering;
    filtering_settings: string;
    filtering_type: FilteringType;
    filtering_types: FilteringType[];
    merge_duplicate_headers: boolean;
    navigation: Navigation;
    n_fixed_columns: number;
    n_fixed_rows: number;
    row_conditional_styles: any[];
    row_deletable: boolean;
    row_selectable: RowSelection;
    row_static_style: any;
    selected_cell: SelectedCells;
    selected_rows: number[];
    sorting: Sorting;
    sorting_settings: SortSettings;
    sorting_type: SortingType;
    table_style: IStylesheetRule[];
    sorting_treat_empty_string_as_none: boolean;
    pagination_mode: PaginationMode;
    pagination_settings: IPaginationSettings;
}

interface IDerivedProps {
    derived_viewport_dataframe: Dataframe;
    derived_viewport_indices: Indices;
    derived_virtual_dataframe: Dataframe;
    derived_virtual_indices: Indices;
}

export type PropsWithDefaults = IProps & IDefaultProps;
export type PropsWithDefaultsAndDerived = PropsWithDefaults & IDerivedProps;

export type ControlledTableProps = PropsWithDefaults & {
    setProps: SetProps;

    columns: VisibleColumns;
    paginator: IPaginator;
    viewport: IDerivedDataframe;
    virtual: IDerivedDataframe;
};

export interface ICellFactoryOptions {
    active_cell: ActiveCell;
    columns: VisibleColumns;
    column_conditional_dropdowns: any[];
    column_conditional_styles: any[];
    column_static_dropdown: any;
    column_static_style: any;
    dataframe: Dataframe;
    dropdown_properties: any; // legacy
    editable: boolean;
    id: string;
    is_focused?: boolean;
    n_fixed_columns: number;
    n_fixed_rows: number;
    paginator: IPaginator;
    row_deletable: boolean;
    row_selectable: RowSelection;
    selected_cell: SelectedCells;
    selected_rows: number[];
    setProps: SetProps;
    viewport: IDerivedDataframe;
}