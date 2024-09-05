import {SortBy} from 'core/sorting';
import {IPaginator} from 'dash-table/derived/paginator';
import {
    Table,
    BasicFilters,
    Cells,
    DataCells,
    Headers,
    Style
} from 'dash-table/derived/style/props';
import {ConditionalTooltip, Tooltip} from 'dash-table/tooltips/props';
import {SingleColumnSyntaxTree} from 'dash-table/syntax-tree';
import {IConditionalElement, INamedElement} from 'dash-table/conditional';
import {Merge} from 'core/type';

export enum ColumnType {
    Any = 'any',
    Numeric = 'numeric',
    Text = 'text',
    Datetime = 'datetime'
}

export enum ExportColumns {
    All = 'all',
    Visible = 'visible'
}

export enum ExportFormat {
    Csv = 'csv',
    Xlsx = 'xlsx',
    None = 'none'
}

export enum ExportHeaders {
    Ids = 'ids',
    Names = 'names',
    None = 'none',
    Display = 'display'
}

export enum FilterCase {
    Insensitive = 'insensitive',
    Sensitive = 'sensitive'
}

export enum SortMode {
    Single = 'single',
    Multi = 'multi'
}

export enum TableAction {
    Custom = 'custom',
    Native = 'native',
    None = 'none'
}

export interface IFilterOptions {
    case?: FilterCase;
    placeholder_text?: string;
}

export interface IDerivedData {
    data: Data;
    indices: Indices;
}

export enum FilterLogicalOperator {
    And = 'and',
    Or = 'or'
}

export interface IFilterAction {
    type: TableAction;
    operator: FilterLogicalOperator;
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

export interface ICellCoordinates {
    row: number;
    column: number;
    row_id?: RowId;
    column_id: ColumnId;
}

export class Column implements IBaseColumn {
    clearable?: boolean | boolean[] | 'first' | 'last' | undefined;
    deletable?: boolean | boolean[] | 'first' | 'last' | undefined;
    editable = false;
    filter_options!: IFilterOptions;
    hideable?: boolean | boolean[] | 'first' | 'last' | undefined;
    renamable?: boolean | boolean[] | 'first' | 'last' | undefined;
    selectable?: boolean | boolean[] | 'first' | 'last' | undefined;
    sort_as_null: SortAsNull = [];
    id!: string;
    name: string | string[] = [];

    constructor(initialValues: any) {
        if (Object.keys(initialValues).includes('name'))
            this.name = initialValues.name;
        if (Object.keys(initialValues).includes('id'))
            this.id = initialValues.id;
    }
}

export type ColumnId = string;
export type Columns = IColumn[];
export type Data = Datum[];
export type IndexedData = IndexedDatum[];
export type Datum = IDatumObject;
export type IndexedDatum = Omit<Datum, 'id'> & {id: number | string};
export type Indices = number[];
export type RowId = string | number;
export type SelectedCells = ICellCoordinates[];
export type Selection = 'single' | 'multi' | false;
export type SetProps = (...args: any[]) => void;
export type SetState = (state: Partial<IState>) => void;
export type SortAsNull = (string | number | boolean)[];

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
    Input = 'input',
    Markdown = 'markdown'
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

export interface IMarkdownOptions {
    link_target: '_blank' | '_parent' | '_self' | '_top' | string;
    html?: boolean;
}

export type NumberFormat =
    | {
          locale: INumberLocale;
          nully: any;
          prefix?: number;
          specifier: string;
      }
    | undefined;

export interface INumberColumn extends ITypeColumn {
    format?: NumberFormat;
    presentation?: Presentation.Input | Presentation.Dropdown;
    type: ColumnType.Numeric;
}

export interface ITextColumn extends ITypeColumn {
    presentation?:
        | Presentation.Input
        | Presentation.Dropdown
        | Presentation.Markdown;
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

export interface IBaseColumn {
    clearable?: boolean | boolean[] | 'first' | 'last';
    deletable?: boolean | boolean[] | 'first' | 'last';
    editable: boolean;
    filter_options: IFilterOptions;
    hideable?: boolean | boolean[] | 'first' | 'last';
    renamable?: boolean | boolean[] | 'first' | 'last';
    selectable?: boolean | boolean[] | 'first' | 'last';
    sort_as_null: SortAsNull;
    id: ColumnId;
    name: string | string[];
}

export interface ILoadingState {
    is_loading: boolean;
    prop_name: string | undefined;
    component_name: string | undefined;
}

export type ConditionalDropdowns = IConditionalDropdown[];
export type DataDropdowns = Partial<IDataDropdowns>[];
export type DataTooltips = Partial<ITableDataTooltips>[];

export type StaticDropdowns = Partial<IStaticDropdowns>;

export type Fixed = {headers: false; data?: 0} | {headers: true; data?: number};
export type IColumnType =
    | INumberColumn
    | ITextColumn
    | IDatetimeColumn
    | IAnyColumn;
export type IColumn = IBaseColumn & IColumnType;

interface IDatumObject {
    [key: string]: boolean | number | string | null | undefined;
}

export interface IDropdownValue {
    label: string;
    value: string | number | boolean;
}

export interface IDropdown {
    clearable?: boolean;
    options: IDropdownValue[];
}

export interface IConditionalDropdown extends IDropdown {
    if: Partial<IConditionalElement & INamedElement>;
}

export interface IDataDropdowns {
    [key: string]: IDropdown;
}

export interface IStaticDropdowns {
    [key: string]: IDropdown;
}

export interface ITableDataTooltips {
    [key: string]: Tooltip;
}

export interface ITableHeaderTooltips {
    [key: string]: (Tooltip | null)[] | Tooltip;
}

export interface ITableStaticTooltips {
    [key: string]: Tooltip;
}

interface IStylesheetRule {
    selector: string;
    rule: string;
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
    header: boolean;
    id: ColumnId;
    row: number;
}

export interface IState {
    activeMenu?: 'show/hide';
    applyFocus?: boolean;
    currentTooltip?: IUSerInterfaceTooltip;
    rawFilterQuery: string;
    scrollbarWidth: number;
    uiCell?: IUserInterfaceCell;
    uiHeaders?: IUserInterfaceCell[];
    uiViewport?: IUserInterfaceViewport;
    workFilter: {
        value: string;
        map: Map<string, SingleColumnSyntaxTree>;
    };
}

export type StandaloneState = IState & Partial<SanitizedAndDerivedProps>;

export interface IProps {
    data_previous?: any[];
    data_timestamp?: number;
    end_cell?: ICellCoordinates;
    is_focused?: boolean;
    start_cell?: ICellCoordinates;

    id: string;

    tooltip: ITableStaticTooltips;
    tooltip_conditional: ConditionalTooltip[];
    tooltip_data?: DataTooltips;
    tooltip_delay: number | null;
    tooltip_duration: number | null;
    tooltip_header?: ITableHeaderTooltips;

    active_cell?: ICellCoordinates;
    cell_selectable?: boolean;
    column_selectable?: Selection;
    columns?: Columns;
    dropdown?: StaticDropdowns;
    dropdown_conditional?: ConditionalDropdowns;
    dropdown_data: DataDropdowns;
    css?: IStylesheetRule[];
    data?: Data;
    editable?: boolean;
    fill_width?: boolean;
    filter_options?: IFilterOptions;
    filter_query?: string;
    filter_action?: TableAction | IFilterAction;
    hidden_columns?: string[];
    include_headers_on_copy_paste?: boolean;
    locale_format: INumberLocale;
    markdown_options: IMarkdownOptions;
    merge_duplicate_headers?: boolean;
    fixed_columns?: Fixed;
    fixed_rows?: Fixed;
    row_deletable?: boolean;
    row_selectable?: Selection;
    selected_cells?: SelectedCells;
    selected_columns?: string[];
    selected_rows?: Indices;
    selected_row_ids?: RowId[];
    setProps?: SetProps;
    sort_action?: TableAction;
    sort_by?: SortBy;
    sort_mode?: SortMode;
    sort_as_null?: SortAsNull;
    style_as_list_view?: boolean;
    page_action?: TableAction;
    page_current?: number;
    page_count?: number;
    page_size: number;

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

    loading_state?: ILoadingState;
}

interface IDefaultProps {
    cell_selectable: boolean;
    column_selectable: Selection;
    css: IStylesheetRule[];
    dropdown: StaticDropdowns;
    dropdown_conditional: ConditionalDropdowns;
    dropdown_data: DataDropdowns;
    editable: boolean;
    end_cell: ICellCoordinates;
    export_columns: ExportColumns;
    export_format: ExportFormat;
    export_headers: ExportHeaders;
    fill_width: boolean;
    filter_options?: IFilterOptions;
    filter_query: string;
    filter_action: TableAction;
    fixed_columns: Fixed;
    fixed_rows: Fixed;
    include_headers_on_copy_paste: boolean;
    merge_duplicate_headers: boolean;
    row_deletable: boolean;
    row_selectable: Selection;
    selected_cells: SelectedCells;
    selected_columns: string[];
    selected_row_ids: RowId[];
    selected_rows: Indices;
    sort_action: TableAction;
    sort_by: SortBy;
    sort_mode: SortMode;
    sort_as_null: SortAsNull;
    start_cell: ICellCoordinates;
    style_as_list_view: boolean;
    tooltip_data: DataTooltips;
    tooltip_header: ITableHeaderTooltips;

    page_action: TableAction;
    page_current: number;
    page_size: number;

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
    derived_filter_query_structure: object | null;
    derived_viewport_data: Data;
    derived_viewport_indices: Indices;
    derived_viewport_row_ids: RowId[];
    derived_viewport_selected_columns: string[];
    derived_viewport_selected_rows: Indices;
    derived_viewport_selected_row_ids: RowId[];
    derived_virtual_data: Data;
    derived_virtual_indices: Indices;
    derived_virtual_row_ids: RowId[];
    derived_virtual_selected_rows: Indices;
    derived_virtual_selected_row_ids: RowId[];
}

export type PropsWithDefaults = IProps & IDefaultProps;

export type SanitizedProps = Omit<
    Omit<
        Merge<
            PropsWithDefaults,
            {
                columns: Columns;
                data: Data;
                filter_action: IFilterAction;
                fixed_columns: number;
                fixed_rows: number;
                loading_state: boolean;
                visibleColumns: Columns;
            }
        >,
        'locale_format'
    >,
    'sort_as_null'
>;

export type SanitizedAndDerivedProps = SanitizedProps & IDerivedProps;

export type ControlledTableProps = SanitizedProps &
    IState & {
        setProps: SetProps;
        setState: SetState;

        currentTooltip: IUSerInterfaceTooltip;
        paginator: IPaginator;
        viewport: IDerivedData;
        viewport_selected_columns: string[];
        viewport_selected_rows: Indices;
        virtual: IDerivedData;
        virtual_selected_rows: Indices;
        virtualized: IVirtualizedDerivedData;
    };

export type SetFilter = (
    filter_query: string,
    rawFilter: string,
    map: Map<string, SingleColumnSyntaxTree>
) => void;

export interface IFilterFactoryProps {
    filter_query: string;
    filter_action: IFilterAction;
    id: string;
    map: Map<string, SingleColumnSyntaxTree>;
    rawFilterQuery: string;
    row_deletable: boolean;
    row_selectable: Selection;
    setFilter: SetFilter;
    style_cell: Style;
    style_cell_conditional: Cells;
    style_filter: Style;
    style_filter_conditional: BasicFilters;
    toggleFilterOptions: (column: IColumn) => IColumn;
    visibleColumns: Columns;
}

export type HeaderFactoryProps = ControlledTableProps & {
    map: Map<string, SingleColumnSyntaxTree>;
    setFilter: SetFilter;
};

export interface ICellFactoryProps {
    active_cell?: ICellCoordinates;
    applyFocus?: boolean;
    cell_selectable: boolean;
    dropdown: StaticDropdowns;
    dropdown_conditional: ConditionalDropdowns;
    dropdown_data: DataDropdowns;
    tooltip: ITableStaticTooltips;
    currentTooltip: IUSerInterfaceTooltip;
    data: Data;
    editable: boolean;
    end_cell: ICellCoordinates;
    fixed_columns: number;
    fixed_rows: number;
    id: string;
    is_focused?: boolean;
    loading_state: boolean;
    markdown_options: IMarkdownOptions;
    paginator: IPaginator;
    row_deletable: boolean;
    row_selectable: Selection;
    selected_cells: SelectedCells;
    selected_rows: Indices;
    setProps: SetProps;
    setState: SetState;
    start_cell: ICellCoordinates;
    style_cell: Style;
    style_data: Style;
    style_filter: Style;
    style_header: Style;
    style_cell_conditional: Cells;
    style_data_conditional: DataCells;
    style_filter_conditional: BasicFilters;
    style_header_conditional: Headers;
    style_table: Table;
    tooltip_data: DataTooltips;
    tooltip_header: ITableHeaderTooltips;
    uiCell?: IUserInterfaceCell;
    uiViewport?: IUserInterfaceViewport;
    viewport: IDerivedData;
    virtualization: boolean;
    virtualized: IVirtualizedDerivedData;
    visibleColumns: Columns;
}
