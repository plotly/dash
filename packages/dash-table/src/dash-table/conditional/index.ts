import { ColumnId, Datum } from 'dash-table/components/Table/props';
import SyntaxTree from 'core/syntax-tree';

export interface IConditionalElement {
    filter?: string;
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

export type ConditionalBasicFilter = INamedElement;
export type ConditionalDataCell = IConditionalElement & IIndexedRowElement & INamedElement;
export type ConditionalCell = INamedElement;
export type ConditionalHeader = IIndexedHeaderElement & INamedElement;

function ifAstFilter(ast: SyntaxTree, datum: Datum) {
    return ast.isValid && ast.evaluate(datum);
}

export function ifColumnId(condition: INamedElement | undefined, columnId: ColumnId) {
    return !condition ||
        condition.column_id === undefined ||
        condition.column_id === columnId;
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
        condition.filter === undefined ||
        ifAstFilter(new SyntaxTree(condition.filter), datum);
}