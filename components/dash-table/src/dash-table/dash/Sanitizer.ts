import * as R from 'ramda';

import {memoizeOne} from 'core/memoizer';
import {
    ColumnType,
    Fixed,
    IColumn,
    INumberLocale,
    PropsWithDefaults,
    Selection,
    SanitizedProps,
    SortAsNull,
    TableAction,
    ExportFormat,
    ExportHeaders,
    IFilterAction,
    FilterLogicalOperator,
    SelectedCells,
    FilterCase,
    IFilterOptions,
    Data
} from 'dash-table/components/Table/props';
import headerRows from 'dash-table/derived/header/headerRows';
import resolveFlag from 'dash-table/derived/cell/resolveFlag';
import dataLoading from 'dash-table/derived/table/data_loading';
import {Column, Columns} from '../components/Table/props';

const D3_DEFAULT_LOCALE: INumberLocale = {
    symbol: ['$', ''],
    decimal: '.',
    group: ',',
    grouping: [3],
    percent: '%',
    separate_4digits: true
};

const DEFAULT_NULLY = '';
const DEFAULT_SPECIFIER = '';
const NULL_SELECTED_CELLS: SelectedCells = [];
const DEFAULT_FILTER_PLACEHOLDER_TEXT = 'filter data...';

const DEFAULT_FILTER_OPTIONS = {
    case: FilterCase.Sensitive,
    placeholder_text: DEFAULT_FILTER_PLACEHOLDER_TEXT
};

const data2number = (data?: any) => +data || 0;

const getFixedColumns = (
    fixed: Fixed,
    row_deletable: boolean,
    row_selectable: Selection
) =>
    !fixed.headers
        ? 0
        : (row_deletable ? 1 : 0) +
          (row_selectable ? 1 : 0) +
          data2number(fixed.data);

const getFixedRows = (
    fixed: Fixed,
    columns: IColumn[],
    filter_action: TableAction
) =>
    !fixed.headers
        ? 0
        : headerRows(columns) +
          (filter_action !== TableAction.None ? 1 : 0) +
          data2number(fixed.data);

const populateColumnsFromData = (data: Data) =>
    data.length > 0
        ? Object.keys(data[0]).map(key => new Column({name: key, id: key}))
        : [];

const applyDefaultsToColumns = (
    defaultLocale: INumberLocale,
    defaultSort: SortAsNull,
    columns: Columns,
    editable: boolean,
    filterOptions: IFilterOptions | undefined
) =>
    R.map(column => {
        const c = R.clone(column);
        c.editable = resolveFlag(editable, column.editable);
        c.filter_options = {
            ...DEFAULT_FILTER_OPTIONS,
            ...(filterOptions ?? {}),
            ...(c.filter_options ?? {})
        };
        c.sort_as_null = c.sort_as_null || defaultSort;

        if (c.type === ColumnType.Numeric && c.format) {
            c.format.locale = getLocale(defaultLocale, c.format.locale);
            c.format.nully = getNully(c.format.nully);
            c.format.specifier = getSpecifier(c.format.specifier);
        }
        return c;
    }, columns);

const applyDefaultToLocale = (locale: INumberLocale) => getLocale(locale);

const getFilterAction = (action: TableAction | IFilterAction): IFilterAction =>
    typeof action === 'object'
        ? {
              type: action.type ?? TableAction.None,
              operator: action.operator ?? FilterLogicalOperator.And
          }
        : {type: action, operator: FilterLogicalOperator.And};

const getVisibleColumns = (
    columns: Columns,
    hiddenColumns: string[] | undefined
) =>
    R.filter(
        column => !hiddenColumns || hiddenColumns.indexOf(column.id) < 0,
        columns
    );

export default class Sanitizer {
    sanitize(props: PropsWithDefaults): SanitizedProps {
        const locale_format = this.applyDefaultToLocale(props.locale_format);
        const data = props.data ?? [];
        const columns = props.columns
            ? this.applyDefaultsToColumns(
                  locale_format,
                  props.sort_as_null,
                  props.columns,
                  props.editable,
                  props.filter_options
              )
            : this.populateColumnsFrom(data);
        const visibleColumns = this.getVisibleColumns(
            columns,
            props.hidden_columns
        );

        let headerFormat = props.export_headers;
        if (
            props.export_format === ExportFormat.Xlsx &&
            R.isNil(headerFormat)
        ) {
            headerFormat = ExportHeaders.Names;
        } else if (
            props.export_format === ExportFormat.Csv &&
            R.isNil(headerFormat)
        ) {
            headerFormat = ExportHeaders.Ids;
        }

        const active_cell = props.cell_selectable
            ? props.active_cell
            : undefined;

        const selected_cells = props.cell_selectable
            ? props.selected_cells
            : NULL_SELECTED_CELLS;

        return R.mergeRight(props, {
            active_cell,
            columns,
            data,
            export_headers: headerFormat,
            filter_action: this.getFilterAction(props.filter_action),
            fixed_columns: getFixedColumns(
                props.fixed_columns,
                props.row_deletable,
                props.row_selectable
            ),
            fixed_rows: getFixedRows(
                props.fixed_rows,
                columns,
                props.filter_action
            ),
            loading_state: dataLoading(props.loading_state),
            locale_format,
            selected_cells,
            visibleColumns
        });
    }

    private readonly populateColumnsFrom = memoizeOne(populateColumnsFromData);

    private readonly applyDefaultToLocale = memoizeOne(applyDefaultToLocale);

    private readonly applyDefaultsToColumns = memoizeOne(
        applyDefaultsToColumns
    );

    private readonly getFilterAction = memoizeOne(getFilterAction);
    private readonly getVisibleColumns = memoizeOne(getVisibleColumns);
}

export const getLocale = (
    ...locales: Partial<INumberLocale>[]
): INumberLocale =>
    R.mergeAll([D3_DEFAULT_LOCALE, ...locales]) as INumberLocale;

export const getSpecifier = (specifier?: string) =>
    specifier === undefined ? DEFAULT_SPECIFIER : specifier;

export const getNully = (nully?: any) =>
    nully === undefined ? DEFAULT_NULLY : nully;
