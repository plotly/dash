import { SortSettings } from 'core/sorting';
import AbstractVirtualizationStrategy from 'dash-table/virtualization/AbstractStrategy';

export type ActiveCell = CellCoordinates | [];
export type CellCoordinates = [number, number];
export type Columns = IColumn[];
export type Dataframe = Datum[];
export type Datum =  IDatumObject | any;
export type Filtering = 'fe' | 'be' | boolean;
export type Indices = number[];
export type Navigation = 'page';
export type RowSelection = 'single' | 'multi' | false;
export type SelectedCells = CellCoordinates[];
export type SetProps = (...args: any[]) => void;
export type Sorting = 'fe' | 'be' | boolean;
export type SortingType = 'multi' | 'single';
export type Virtualization = 'fe' | 'be' | boolean;

interface IColumn {
    id: string | number;
    editable?: boolean;
    options?: { label: string | number, value: any }[]; // legacy
    [key: string]: any;
}

interface IDatumObject {
    [key: string]: any;
}

export interface IVirtualizationSettings {
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
    dataframe?: Dataframe;
    dropdown_properties: any; // legacy
    editable?: boolean;
    filtering?: Filtering;
    filtering_settings?: string;
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
    table_style?: { selector: string, rule: string }[];
    sorting_treat_empty_string_as_none?: boolean;
    virtualization?: Virtualization;
    virtualization_settings?: IVirtualizationSettings;
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
    table_style: { selector: string, rule: string }[];
    sorting_treat_empty_string_as_none: boolean;
    virtual_dataframe: Dataframe;
    virtual_dataframe_indices: Indices;
    virtualization: Virtualization;
    virtualization_settings: IVirtualizationSettings;
}

export type PropsWithDefaults = IProps & IDefaultProps;

export type ControlledTableProps = PropsWithDefaults & {
    setProps: SetProps;
    virtualizer: AbstractVirtualizationStrategy
};

export interface ICellFactoryOptions {
    active_cell: ActiveCell;
    columns: Columns;
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
    row_deletable: boolean;
    row_selectable: RowSelection;
    selected_cell: SelectedCells;
    selected_rows: number[];
    setProps: SetProps;
    virtual_dataframe: Dataframe;
    virtual_dataframe_indices: Indices;
    virtualizer: AbstractVirtualizationStrategy;
}