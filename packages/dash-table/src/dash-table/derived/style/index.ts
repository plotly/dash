import * as R from 'ramda';
import { CSSProperties } from 'react';

import SyntaxTree from 'core/syntax-tree';
import { memoizeOneFactory } from 'core/memoizer';

import { Datum, IVisibleColumn } from 'dash-table/components/Table/props';

import { Style, IConditionalElement, INamedElement, CellsAndHeaders, Cells, Headers, Table, IIndexedHeaderElement, IIndexedRowElement } from './props';
import converter, { StyleProperty } from './py2jsCssProperties';

export interface IConvertedStyle {
    style: CSSProperties;
    matchesColumn: (column: IVisibleColumn) => boolean;
    matchesRow: (index: number) => boolean;
    matchesFilter: (datum: Datum) => boolean;
}

type GenericIf = Partial<IConditionalElement & IIndexedHeaderElement & IIndexedRowElement & INamedElement>;
type GenericStyle = Style & Partial<{ if: GenericIf }>;

function convertElement(style: GenericStyle) {
    const indexFilter = style.if && (style.if.header_index || style.if.row_index);
    let ast: SyntaxTree;

    return {
        matchesColumn: (column: IVisibleColumn) =>
            !style.if ||
            !style.if.column_id ||
            style.if.column_id === column.id,
        matchesRow: (index: number) =>
            indexFilter === undefined ?
                true :
                typeof indexFilter === 'number' ?
                    index === indexFilter :
                    indexFilter === 'odd' ? index % 2 === 1 : index % 2 === 0,
        matchesFilter: (datum: Datum) =>
            !style.if ||
            style.if.filter === undefined ||
            (ast = ast || new SyntaxTree(style.if.filter)).evaluate(datum),
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

export const derivedRelevantCellStyles = memoizeOneFactory(
    (cellsAndHeaders: CellsAndHeaders, cells: Cells) => R.concat(
        R.map(convertElement, cellsAndHeaders || []),
        R.map(convertElement, cells || [])
    )
);

export const derivedRelevantHeaderStyles = memoizeOneFactory(
    (cellsAndHeaders: CellsAndHeaders, headers: Headers) => R.concat(
        R.map(convertElement, cellsAndHeaders || []),
        R.map(convertElement, headers || [])
    )
);

export const derivedTableStyle = memoizeOneFactory(
    (table: Table) => convertStyle(table || {})
);