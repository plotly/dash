import { ColumnId } from 'dash-table/components/Table/props';
import IStyle from './IStyle';

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

type ConditionalBasicFilter = INamedElement;
type ConditionalDataCell = IConditionalElement & IIndexedRowElement & INamedElement;
type ConditionalCell = INamedElement;
type ConditionalHeader = IIndexedHeaderElement & INamedElement;

export { IStyle };

export type Style = Partial<IStyle>;

export type BasicFilter = Style & { if: ConditionalBasicFilter };
export type DataCell = Style & { if: ConditionalDataCell };
export type Cell = Style & { if: ConditionalCell };
export type Header = Style & { if: ConditionalHeader };

export type BasicFilters = BasicFilter[];
export type DataCells = DataCell[];
export type Cells = Cell[];
export type Headers = Header[];
export type Table = Style;