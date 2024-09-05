import {
    ConditionalBasicFilter,
    ConditionalDataCell,
    ConditionalCell,
    ConditionalHeader
} from 'dash-table/conditional';

import IStyle from './IStyle';

export {IStyle};

export type Style = Partial<IStyle>;

export type BasicFilter = Style & {if: ConditionalBasicFilter};
export type DataCell = Style & {if: ConditionalDataCell};
export type Cell = Style & {if: ConditionalCell};
export type Header = Style & {if: ConditionalHeader};

export type BasicFilters = BasicFilter[];
export type DataCells = DataCell[];
export type Cells = Cell[];
export type Headers = Header[];

export type Table = Style;
