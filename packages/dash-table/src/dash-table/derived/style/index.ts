import * as R from 'ramda';
import { CSSProperties } from 'react';

import { memoizeOneFactory } from 'core/memoizer';

import { Datum, IVisibleColumn } from 'dash-table/components/Table/props';

import {
    Cells,
    DataCells,
    BasicFilters,
    Headers,
    Style,
    Table
} from './props';
import converter, { StyleProperty } from './py2jsCssProperties';

import {
    IConditionalElement,
    IIndexedHeaderElement,
    IIndexedRowElement,
    INamedElement,
    ITypedElement,
    ifColumnId,
    ifColumnType
 } from 'dash-table/conditional';
import { QuerySyntaxTree } from 'dash-table/syntax-tree';

export interface IConvertedStyle {
    style: CSSProperties;
    matchesColumn: (column: IVisibleColumn) => boolean;
    matchesRow: (index: number) => boolean;
    matchesFilter: (datum: Datum) => boolean;
}

type GenericIf = Partial<IConditionalElement & IIndexedHeaderElement & IIndexedRowElement & INamedElement & ITypedElement>;
type GenericStyle = Style & Partial<{ if: GenericIf }>;

function convertElement(style: GenericStyle) {
    const indexFilter = style.if && (style.if.header_index || style.if.row_index);
    let ast: QuerySyntaxTree;

    return {
        matchesColumn: (column: IVisibleColumn) =>
            !style.if || (
                ifColumnId(style.if, column.id) &&
                ifColumnType(style.if, column.type)
            ),
        matchesRow: (index: number) =>
            indexFilter === undefined ?
                true :
                typeof indexFilter === 'number' ?
                    index === indexFilter :
                    indexFilter === 'odd' ? index % 2 === 1 : index % 2 === 0,
        matchesFilter: (datum: Datum) =>
            !style.if ||
            style.if.filter === undefined ||
            (ast = ast || new QuerySyntaxTree(style.if.filter)).evaluate(datum),
        style: convertStyle(style)
    };
}

function convertStyle(style: Style): CSSProperties {
    return R.reduce<[string, StyleProperty?], any>((res, [key, value]) => {
        if (converter.has(key)) {
            res[converter.get(key) as string] = value;
        }
        return res;
    }, {}, R.toPairs(style));
}

export const derivedRelevantCellStyles = memoizeOneFactory((
    cell: Style,
    dataCell: Style,
    cells: Cells,
    dataCells: DataCells
) => R.concat(
    R.concat(
        cell ? [convertElement(cell)] : [],
        R.map(convertElement, cells || [])
    ),
    R.concat(
        dataCell ? [convertElement(dataCell)] : [],
        R.map(convertElement, dataCells || [])
    )
));

export const derivedRelevantFilterStyles = memoizeOneFactory((
    cell: Style,
    filter: Style,
    cells: Cells,
    filters: BasicFilters
) => R.concat(
    R.concat(
        cell ? [convertElement(cell)] : [],
        R.map(convertElement, cells || [])
    ),
    R.concat(
        filter ? [convertElement(filter)] : [],
        R.map(convertElement, filters || [])
    )
));

export const derivedRelevantHeaderStyles = memoizeOneFactory((
    cell: Style,
    header: Style,
    cells: Cells,
    headers: Headers
) => R.concat(
    R.concat(
        cell ? [convertElement(cell)] : [],
        R.map(convertElement, cells || [])
    ),
    R.concat(
        header ? [convertElement(header)] : [],
        R.map(convertElement, headers || [])
    )
));

export const derivedTableStyle = memoizeOneFactory(
    (defaultTable: Table, table: Table) => [
        convertStyle(defaultTable),
        convertStyle(table)
    ]
);