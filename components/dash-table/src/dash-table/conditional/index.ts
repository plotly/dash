import * as R from 'ramda';

import {
    ColumnId,
    Datum,
    ColumnType,
    IColumn
} from 'dash-table/components/Table/props';
import {QuerySyntaxTree} from 'dash-table/syntax-tree';
import {IConvertedStyle} from 'dash-table/derived/style';

export interface IConditionalElement {
    filter_query?: string;
}

export interface IIndexedHeaderElement {
    header_index?: number | 'odd' | 'even';
}

export interface IIndexedRowElement {
    row_index?: number[] | number | 'odd' | 'even';
}

export interface INamedElement {
    column_id?: ColumnId[] | ColumnId;
}

export interface IStateElement {
    state?: 'active' | 'selected';
}

export interface ITypedElement {
    column_type?: ColumnType;
}

export interface IEditableElement {
    column_editable?: boolean;
}

export type ConditionalBasicFilter = INamedElement & ITypedElement;
export type ConditionalDataCell = IConditionalElement &
    IIndexedRowElement &
    INamedElement &
    IStateElement &
    ITypedElement &
    IEditableElement;
export type ConditionalCell = INamedElement & ITypedElement;
export type ConditionalHeader = IIndexedHeaderElement &
    INamedElement &
    ITypedElement;

function ifAstFilter(ast: QuerySyntaxTree, datum: Datum) {
    return ast.isValid && ast.evaluate(datum);
}

export function ifColumnStateActive(
    condition: IStateElement | undefined,
    active: boolean
) {
    return condition?.state !== 'active' || active;
}

export function ifColumnStateSelected(
    condition: IStateElement | undefined,
    selected: boolean
) {
    return condition?.state !== 'selected' || selected;
}

export function ifColumnId(
    condition: INamedElement | undefined,
    columnId: ColumnId
) {
    if (!condition || condition.column_id === undefined) {
        return true;
    }

    return Array.isArray(condition.column_id)
        ? R.includes(columnId, condition.column_id)
        : condition.column_id === columnId;
}

export function ifColumnType(
    condition: ITypedElement | undefined,
    columnType?: ColumnType
) {
    return (
        !condition ||
        condition.column_type === undefined ||
        condition.column_type === (columnType || ColumnType.Any)
    );
}

export function ifRowIndex(
    condition: IIndexedRowElement | undefined,
    rowIndex: number
) {
    if (!condition || condition.row_index === undefined) {
        return true;
    }

    const rowCondition = condition.row_index;
    return typeof rowCondition === 'string'
        ? rowIndex % 2 === (rowCondition === 'odd' ? 1 : 0)
        : Array.isArray(rowCondition)
        ? R.includes(rowIndex, rowCondition)
        : rowIndex === rowCondition;
}

export function ifHeaderIndex(
    condition: IIndexedHeaderElement | undefined,
    headerIndex: number
) {
    if (!condition || condition.header_index === undefined) {
        return true;
    }

    const headerCondition = condition.header_index;
    return typeof headerCondition === 'string'
        ? headerIndex % 2 === (headerCondition === 'odd' ? 1 : 0)
        : Array.isArray(headerCondition)
        ? R.includes(headerIndex, headerCondition)
        : headerIndex === headerCondition;
}

export function ifFilter(
    condition: IConditionalElement | undefined,
    datum: Datum
) {
    return (
        !condition ||
        condition.filter_query === undefined ||
        ifAstFilter(new QuerySyntaxTree(condition.filter_query), datum)
    );
}

export function ifEditable(
    condition: IEditableElement | undefined,
    isEditable: boolean
) {
    if (!condition || condition.column_editable === undefined) {
        return true;
    }
    return isEditable === condition.column_editable;
}

export type Filter<T> = (s: T[]) => T[];

export const matchesDataCell = (
    datum: Datum,
    i: number,
    column: IColumn,
    active: boolean,
    selected: boolean
): Filter<IConvertedStyle> =>
    R.filter<IConvertedStyle>(
        style =>
            !style.checksHeaderRow() &&
            style.matchesActive(active) &&
            style.matchesSelected(selected) &&
            style.matchesDataRow(i) &&
            style.matchesColumn(column) &&
            style.matchesFilter(datum)
    );

export const matchesFilterCell = (column: IColumn): Filter<IConvertedStyle> =>
    R.filter<IConvertedStyle>(
        style =>
            !style.checksState() &&
            !style.checksDataRow() &&
            !style.checksHeaderRow() &&
            style.matchesColumn(column)
    );

export const matchesHeaderCell = (
    i: number,
    column: IColumn
): Filter<IConvertedStyle> =>
    R.filter<IConvertedStyle>(
        style =>
            !style.checksState() &&
            !style.checksDataRow() &&
            style.matchesHeaderRow(i) &&
            style.matchesColumn(column)
    );

export const matchesDataOpCell = (
    datum: Datum,
    i: number
): Filter<IConvertedStyle> =>
    R.filter<IConvertedStyle>(
        style =>
            !style.checksState() &&
            !style.checksColumn() &&
            !style.checksHeaderRow() &&
            style.matchesDataRow(i) &&
            style.matchesFilter(datum)
    );

export const getFilterOpStyles: Filter<IConvertedStyle> =
    R.filter<IConvertedStyle>(
        style =>
            !style.checksState() &&
            !style.checksDataRow() &&
            !style.checksHeaderRow() &&
            !style.checksColumn()
    );

export const getHeaderOpStyles = (i: number): Filter<IConvertedStyle> =>
    R.filter<IConvertedStyle>(
        style =>
            !style.checksDataRow() &&
            !style.checksState() &&
            !style.checksColumn() &&
            style.matchesHeaderRow(i)
    );
