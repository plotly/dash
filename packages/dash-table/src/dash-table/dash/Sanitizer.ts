
import * as R from 'ramda';

import { memoizeOne } from 'core/memoizer';
import {
    Columns,
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
    ExportHeaders
} from 'dash-table/components/Table/props';
import headerRows from 'dash-table/derived/header/headerRows';
import resolveFlag from 'dash-table/derived/cell/resolveFlag';

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

const data2number = (data?: any) => +data || 0;

const getFixedColumns = (
    fixed: Fixed,
    row_deletable: boolean,
    row_selectable: Selection
) => !fixed.headers ?
        0 :
        (row_deletable ? 1 : 0) + (row_selectable ? 1 : 0) + data2number(fixed.data);

const getFixedRows = (
    fixed: Fixed,
    columns: IColumn[],
    filter_action: TableAction
) => !fixed.headers ?
        0 :
        headerRows(columns) + (filter_action !== TableAction.None ? 1 : 0) + data2number(fixed.data);

const applyDefaultsToColumns = (
    defaultLocale: INumberLocale,
    defaultSort: SortAsNull,
    columns: Columns,
    editable: boolean
) => R.map(column => {
    const c = R.clone(column);
    c.editable = resolveFlag(editable, column.editable);
    c.sort_as_null = c.sort_as_null || defaultSort;

    if (c.type === ColumnType.Numeric && c.format) {
        c.format.locale = getLocale(defaultLocale, c.format.locale);
        c.format.nully = getNully(c.format.nully);
        c.format.specifier = getSpecifier(c.format.specifier);
    }
    return c;
}, columns);

const applyDefaultToLocale = (locale: INumberLocale) => getLocale(locale);

const getVisibleColumns = (
    columns: Columns,
    hiddenColumns: string[] | undefined
) => R.filter(column => !hiddenColumns || hiddenColumns.indexOf(column.id) < 0, columns);

export default class Sanitizer {
    sanitize(props: PropsWithDefaults): SanitizedProps {
        const locale_format = this.applyDefaultToLocale(props.locale_format);
        const columns = this.applyDefaultsToColumns(locale_format, props.sort_as_null, props.columns, props.editable);
        const visibleColumns = this.getVisibleColumns(columns, props.hidden_columns);

        let headerFormat = props.export_headers;
        if (props.export_format === ExportFormat.Xlsx &&  R.isNil(headerFormat)) {
            headerFormat =  ExportHeaders.Names;
        } else if (props.export_format === ExportFormat.Csv && R.isNil(headerFormat)) {
            headerFormat = ExportHeaders.Ids;
        }

        return R.merge(props, {
            columns,
            export_headers: headerFormat,
            fixed_columns: getFixedColumns(props.fixed_columns, props.row_deletable, props.row_selectable),
            fixed_rows: getFixedRows(props.fixed_rows, props.columns, props.filter_action),
            locale_format,
            visibleColumns
        });
    }

    private readonly applyDefaultToLocale = memoizeOne(applyDefaultToLocale);

    private readonly applyDefaultsToColumns = memoizeOne(applyDefaultsToColumns);

    private readonly getVisibleColumns = memoizeOne(getVisibleColumns);
}

export const getLocale = (...locales: Partial<INumberLocale>[]): INumberLocale =>
    R.mergeAll([
        D3_DEFAULT_LOCALE,
        ...locales
    ]) as INumberLocale;

export const getSpecifier = (specifier?: string) => specifier === undefined ?
    DEFAULT_SPECIFIER :
    specifier;

export const getNully = (nully?: any) => nully === undefined ?
    DEFAULT_NULLY :
    nully;