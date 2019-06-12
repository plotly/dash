import * as R from 'ramda';
import React, { CSSProperties } from 'react';

import Logger from 'core/Logger';
import { arrayMap, arrayMap2 } from 'core/math/arrayZipMap';
import memoizerCache from 'core/cache/memoizer';
import { memoizeOne } from 'core/memoizer';

import ColumnFilter from 'dash-table/components/Filter/Column';
import { ColumnId, IVisibleColumn, VisibleColumns, RowSelection, TableAction } from 'dash-table/components/Table/props';
import derivedFilterStyles, { derivedFilterOpStyles } from 'dash-table/derived/filter/wrapperStyles';
import derivedHeaderOperations from 'dash-table/derived/header/operations';
import { derivedRelevantFilterStyles } from 'dash-table/derived/style';
import { BasicFilters, Cells, Style } from 'dash-table/derived/style/props';
import { SingleColumnSyntaxTree, getMultiColumnQueryString } from 'dash-table/syntax-tree';

import { IEdgesMatrices } from 'dash-table/derived/edges/type';
import { updateMap } from 'dash-table/derived/filter/map';

type SetFilter = (
    filter_query: string,
    rawFilter: string,
    map: Map<string, SingleColumnSyntaxTree>
) => void;

export interface IFilterOptions {
    columns: VisibleColumns;
    filter_query: string;
    filter_action: TableAction;
    id: string;
    map: Map<string, SingleColumnSyntaxTree>;
    rawFilterQuery: string;
    row_deletable: boolean;
    row_selectable: RowSelection;
    setFilter: SetFilter;
    style_cell: Style;
    style_cell_conditional: Cells;
    style_filter: Style;
    style_filter_conditional: BasicFilters;
}

const NO_FILTERS: JSX.Element[][] = [];

export default class FilterFactory {
    private readonly filterStyles = derivedFilterStyles();
    private readonly filterOpStyles = derivedFilterOpStyles();
    private readonly relevantStyles = derivedRelevantFilterStyles();
    private readonly headerOperations = derivedHeaderOperations();

    private get props() {
        return this.propsFn();
    }

    constructor(private readonly propsFn: () => IFilterOptions) {

    }

    private onChange = (column: IVisibleColumn, map: Map<string, SingleColumnSyntaxTree>, setFilter: SetFilter, ev: any) => {
        Logger.debug('Filter -- onChange', column.id, ev.target.value && ev.target.value.trim());

        const value = ev.target.value.trim();

        map = updateMap(map, column, value);

        const asts = Array.from(map.values());
        const globalFilter = getMultiColumnQueryString(asts);

        const rawGlobalFilter = R.map(
            ast => ast.query || '',
            R.filter<SingleColumnSyntaxTree>(ast => Boolean(ast), asts)
        ).join(' && ');

        setFilter(globalFilter, rawGlobalFilter, map);
    }

    private filter = memoizerCache<[ColumnId, number]>()((
        column: IVisibleColumn,
        index: number,
        map: Map<string, SingleColumnSyntaxTree>,
        setFilter: SetFilter
    ) => {
        const ast = map.get(column.id.toString());

        return (<ColumnFilter
            key={`column-${index}`}
            classes={`dash-filter column-${index}`}
            columnId={column.id}
            isValid={!ast || ast.isValid}
            setFilter={this.onChange.bind(this, column, map, setFilter)}
            value={ast && ast.query}
        />);
    });

    private wrapperStyles = memoizeOne((
        styles: any[],
        edges: IEdgesMatrices | undefined
    ) => arrayMap(
        styles,
        (s, j) => R.merge(
            s,
            edges && edges.getStyle(0, j)
        )
    ));

    public createFilters(
        filterEdges: IEdgesMatrices | undefined,
        filterOpEdges: IEdgesMatrices | undefined
    ) {
        const {
            columns,
            filter_action,
            map,
            row_deletable,
            row_selectable,
            setFilter,
            style_cell,
            style_cell_conditional,
            style_filter,
            style_filter_conditional
        } = this.props;

        if (filter_action === TableAction.None) {
            return NO_FILTERS;
        }

        const relevantStyles = this.relevantStyles(
            style_cell,
            style_filter,
            style_cell_conditional,
            style_filter_conditional
        );

        const wrapperStyles = this.wrapperStyles(
            this.filterStyles(columns, relevantStyles),
            filterEdges
        );

        const opStyles = this.filterOpStyles(
            1,
            (row_selectable ? 1 : 0) + (row_deletable ? 1 : 0),
            relevantStyles
        )[0];

        const filters = R.addIndex<IVisibleColumn, JSX.Element>(R.map)((column, index) => {
            return this.filter.get(column.id, index)(
                column,
                index,
                map,
                setFilter
            );
        }, columns);

        const styledFilters = this.getFilterCells(
            filters,
            wrapperStyles,
            filterEdges
        );

        const operations = this.headerOperations(
            1,
            row_selectable,
            row_deletable
        )[0];

        const operators = this.getOpFilterCells(
            operations,
            opStyles,
            filterOpEdges
        );

        return this.getCells(operators, styledFilters);
    }

    getCells = memoizeOne((
        opCells: JSX.Element[],
        filterCells: JSX.Element[]
    ) => [opCells.concat(filterCells)]);

    getFilterCells = memoizeOne((
        filters: JSX.Element[],
        styles: (CSSProperties | undefined)[],
        edges: IEdgesMatrices | undefined
    ) => arrayMap2(
        filters,
        styles,
        (f, s, j) => React.cloneElement(f, {
            style: R.mergeAll([
                edges && edges.getStyle(0, j),
                s,
                f.props.style
            ])
        })
    ));

    getOpFilterCells = memoizeOne((
        ops: JSX.Element[],
        styles: (CSSProperties | undefined)[],
        edges: IEdgesMatrices | undefined
    ) => arrayMap2(
        ops,
        styles,
        (o, s, j) => React.cloneElement(o, {
            style: R.mergeAll([
                edges && edges.getStyle(0, j),
                s,
                o.props.style
            ])
        })
    ));
}