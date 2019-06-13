import * as R from 'ramda';

import { ColumnId, Datum, ColumnType, IVisibleColumn } from 'dash-table/components/Table/props';
import { QuerySyntaxTree } from 'dash-table/syntax-tree';
import { IConvertedStyle } from 'dash-table/derived/style';

export interface IConditionalElement {
    filter_query?: string;
}

export interface IIndexedHeaderElement {
    header_index?: number | 'odd' | 'even';
}

export interface IIndexedRowElement {
    row_index?: number | 'odd' | 'even';
}

export interface INamedElement {
    column_id?: ColumnId;
}

export interface ITypedElement {
    column_type?: ColumnType;
}

export interface IEditableElement {
    column_editable?: boolean;
}

export type ConditionalBasicFilter = INamedElement & ITypedElement;
export type ConditionalDataCell = IConditionalElement & IIndexedRowElement & INamedElement & ITypedElement & IEditableElement;
export type ConditionalCell = INamedElement & ITypedElement;
export type ConditionalHeader = IIndexedHeaderElement & INamedElement & ITypedElement;

function ifAstFilter(ast: QuerySyntaxTree, datum: Datum) {
    return ast.isValid && ast.evaluate(datum);
}

export function ifColumnId(condition: INamedElement | undefined, columnId: ColumnId) {
    return !condition ||
        condition.column_id === undefined ||
        condition.column_id === columnId;
}

export function ifColumnType(condition: ITypedElement | undefined, columnType?: ColumnType) {
    return !condition ||
        condition.column_type === undefined ||
        condition.column_type === (columnType || ColumnType.Any);
}

export function ifRowIndex(condition: IIndexedRowElement | undefined, rowIndex: number) {
    if (!condition ||
        condition.row_index === undefined) {
        return true;
    }

    const rowCondition = condition.row_index;
    return typeof rowCondition === 'number' ?
        rowIndex === rowCondition :
        rowCondition === 'odd' ? rowIndex % 2 === 1 : rowIndex % 2 === 0;
}

export function ifHeaderIndex(condition: IIndexedHeaderElement | undefined, headerIndex: number) {
    if (!condition ||
        condition.header_index === undefined) {
        return true;
    }

    const headerCondition = condition.header_index;
    return typeof headerCondition === 'number' ?
        headerIndex === headerCondition :
        headerCondition === 'odd' ? headerIndex % 2 === 1 : headerIndex % 2 === 0;
}

export function ifFilter(condition: IConditionalElement | undefined, datum: Datum) {
    return !condition ||
        condition.filter_query === undefined ||
        ifAstFilter(new QuerySyntaxTree(condition.filter_query), datum);
}

export function ifEditable(condition: IEditableElement | undefined, isEditable: boolean)  {
    if  (!condition ||
        condition.column_editable === undefined) {
            return true;
    }
    return isEditable === condition.column_editable;
}

export type Filter<T> = (s: T[]) => T[];

export const matchesDataCell = (datum: Datum, i: number, column: IVisibleColumn): Filter<IConvertedStyle> => R.filter<IConvertedStyle>((style =>
    style.matchesRow(i) &&
    style.matchesColumn(column) &&
    style.matchesFilter(datum)
));

export const matchesFilterCell = (column: IVisibleColumn): Filter<IConvertedStyle> => R.filter<IConvertedStyle>((style =>
    style.matchesColumn(column)
));

export const matchesHeaderCell = (i: number, column: IVisibleColumn): Filter<IConvertedStyle> => R.filter<IConvertedStyle>((style =>
    style.matchesRow(i) &&
    style.matchesColumn(column)
));

export const matchesDataOpCell = (datum: Datum, i: number): Filter<IConvertedStyle> => R.filter<IConvertedStyle>((style =>
    !style.checksColumn() &&
    style.matchesRow(i) &&
    style.matchesFilter(datum)
));

export const getFilterOpStyles: Filter<IConvertedStyle> = R.filter<IConvertedStyle>((style =>
    !style.checksColumn()
));

export const getHeaderOpStyles = (i: number): Filter<IConvertedStyle> => R.filter<IConvertedStyle>((style =>
    style.matchesRow(i) &&
    !style.checksColumn()
));