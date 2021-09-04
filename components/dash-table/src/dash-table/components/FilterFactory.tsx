import * as R from 'ramda';
import React, {CSSProperties} from 'react';

import Logger from 'core/Logger';
import {arrayMap, arrayMap2} from 'core/math/arrayZipMap';
import memoizerCache from 'core/cache/memoizer';
import {memoizeOne} from 'core/memoizer';

import ColumnFilter from 'dash-table/components/Filter/Column';
import {
    ColumnId,
    IColumn,
    TableAction,
    IFilterFactoryProps,
    SetFilter,
    FilterLogicalOperator
} from 'dash-table/components/Table/props';
import derivedFilterStyles, {
    derivedFilterOpStyles
} from 'dash-table/derived/filter/wrapperStyles';
import derivedHeaderOperations from 'dash-table/derived/header/operations';
import {derivedRelevantFilterStyles} from 'dash-table/derived/style';
import {SingleColumnSyntaxTree} from 'dash-table/syntax-tree';

import {IEdgesMatrices} from 'dash-table/derived/edges/type';
import {updateColumnFilter} from 'dash-table/derived/filter/map';

const NO_FILTERS: JSX.Element[][] = [];

export default class FilterFactory {
    private readonly filterStyles = derivedFilterStyles();
    private readonly filterOpStyles = derivedFilterOpStyles();
    private readonly relevantStyles = derivedRelevantFilterStyles();
    private readonly headerOperations = derivedHeaderOperations();

    private get props() {
        return this.propsFn();
    }

    constructor(private readonly propsFn: () => IFilterFactoryProps) {}

    private onChange = (
        column: IColumn,
        map: Map<string, SingleColumnSyntaxTree>,
        operator: FilterLogicalOperator,
        setFilter: SetFilter,
        ev: any
    ) => {
        Logger.debug(
            'Filter -- onChange',
            column.id,
            ev.target.value && ev.target.value.trim()
        );

        const value = ev.target.value.trim();

        updateColumnFilter(map, column, operator, value, setFilter);
    };

    private onToggleChange = (
        column: IColumn,
        map: Map<string, SingleColumnSyntaxTree>,
        operator: FilterLogicalOperator,
        setFilter: SetFilter,
        toggleFilterOptions: (column: IColumn) => IColumn,
        value: any
    ) => {
        const newColumn = toggleFilterOptions(column);

        updateColumnFilter(map, newColumn, operator, value, setFilter);
    };

    private filter = memoizerCache<[ColumnId, number]>()(
        (
            column: IColumn,
            index: number,
            map: Map<string, SingleColumnSyntaxTree>,
            operator: FilterLogicalOperator,
            setFilter: SetFilter,
            toggleFilterOptions: (column: IColumn) => IColumn
        ) => {
            const ast = map.get(column.id.toString());

            return (
                <ColumnFilter
                    key={`column-${index}`}
                    className={`dash-filter column-${index}`}
                    columnId={column.id}
                    filterOptions={column.filter_options}
                    isValid={!ast || ast.isValid}
                    setFilter={this.onChange.bind(
                        this,
                        column,
                        map,
                        operator,
                        setFilter
                    )}
                    // Running into TypeScript binding issues with many parameters..
                    // bind with no more than 4 params each time.. sigh..
                    toggleFilterOptions={this.onToggleChange
                        .bind(this, column, map, operator, setFilter)
                        .bind(this, toggleFilterOptions, ast && ast.query)}
                    value={ast && ast.query}
                />
            );
        }
    );

    private wrapperStyles = memoizeOne(
        (styles: any[], edges: IEdgesMatrices | undefined) =>
            arrayMap(styles, (s, j) =>
                R.mergeRight(s, (edges && edges.getStyle(0, j)) || {})
            )
    );

    public createFilters(
        filterEdges: IEdgesMatrices | undefined,
        filterOpEdges: IEdgesMatrices | undefined
    ) {
        const {
            filter_action,
            map,
            row_deletable,
            row_selectable,
            setFilter,
            style_cell,
            style_cell_conditional,
            style_filter,
            style_filter_conditional,
            toggleFilterOptions,
            visibleColumns
        } = this.props;

        if (filter_action.type === TableAction.None) {
            return NO_FILTERS;
        }

        const relevantStyles = this.relevantStyles(
            style_cell,
            style_filter,
            style_cell_conditional,
            style_filter_conditional
        );

        const wrapperStyles = this.wrapperStyles(
            this.filterStyles(visibleColumns, relevantStyles),
            filterEdges
        );

        const opStyles = this.filterOpStyles(
            1,
            (row_selectable ? 1 : 0) + (row_deletable ? 1 : 0),
            relevantStyles
        )[0];

        const filters = R.addIndex<IColumn, JSX.Element>(R.map)(
            (column, index) => {
                return this.filter.get(column.id, index)(
                    column,
                    index,
                    map,
                    filter_action.operator,
                    setFilter,
                    toggleFilterOptions
                );
            },
            visibleColumns
        );

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

    getCells = memoizeOne(
        (opCells: JSX.Element[], filterCells: JSX.Element[]) => [
            opCells.concat(filterCells)
        ]
    );

    getFilterCells = memoizeOne(
        (
            filters: JSX.Element[],
            styles: (CSSProperties | undefined)[],
            edges: IEdgesMatrices | undefined
        ) =>
            arrayMap2(filters, styles, (f, s, j) =>
                React.cloneElement(f, {
                    style: R.mergeAll([
                        edges && edges.getStyle(0, j),
                        s,
                        f.props.style
                    ])
                })
            )
    );

    getOpFilterCells = memoizeOne(
        (
            ops: JSX.Element[],
            styles: (CSSProperties | undefined)[],
            edges: IEdgesMatrices | undefined
        ) =>
            arrayMap2(ops, styles, (o, s, j) =>
                React.cloneElement(o, {
                    style: R.mergeAll([
                        edges && edges.getStyle(0, j),
                        s,
                        o.props.style
                    ])
                })
            )
    );
}
