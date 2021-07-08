import * as R from 'ramda';
import React, {CSSProperties} from 'react';

import {matrixMap2, matrixMap3} from 'core/math/matrixZipMap';
import {arrayMap2} from 'core/math/arrayZipMap';

import {
    ICellFactoryProps,
    IMarkdownOptions
} from 'dash-table/components/Table/props';
import derivedCellWrappers from 'dash-table/derived/cell/wrappers';
import derivedCellContents from 'dash-table/derived/cell/contents';
import derivedCellOperations from 'dash-table/derived/cell/operations';
import {
    derivedDataOpStyles,
    derivedDataStyles,
    derivedPartialDataStyles
} from 'dash-table/derived/cell/wrapperStyles';
import derivedDropdowns from 'dash-table/derived/cell/dropdowns';
import {derivedRelevantCellStyles} from 'dash-table/derived/style';
import {IEdgesMatrices} from 'dash-table/derived/edges/type';
import {memoizeOne} from 'core/memoizer';
import memoizerCache from 'core/cache/memoizer';
import Markdown from 'dash-table/utils/Markdown';

export default class CellFactory {
    private get props() {
        return this.propsFn();
    }

    constructor(
        private readonly propsFn: () => ICellFactoryProps,
        private readonly cellContents = derivedCellContents(propsFn),
        private readonly cellDropdowns = derivedDropdowns(),
        private readonly cellOperations = derivedCellOperations(),
        private readonly dataPartialStyles = derivedPartialDataStyles(),
        private readonly dataStyles = derivedDataStyles(),
        private readonly dataOpStyles = derivedDataOpStyles(),
        private readonly cellWrappers = derivedCellWrappers(propsFn),
        private readonly relevantStyles = derivedRelevantCellStyles()
    ) {}

    private getMarkdown = memoizeOne(
        (options: IMarkdownOptions) => new Markdown(options)
    );

    public createCells(
        dataEdges: IEdgesMatrices | undefined,
        dataOpEdges: IEdgesMatrices | undefined
    ) {
        const {
            active_cell,
            applyFocus,
            dropdown_conditional,
            dropdown,
            data,
            dropdown_data,
            id,
            is_focused,
            loading_state,
            markdown_options,
            row_deletable,
            row_selectable,
            selected_cells,
            selected_rows,
            setProps,
            style_cell,
            style_cell_conditional,
            style_data,
            style_data_conditional,
            virtualized,
            visibleColumns
        } = this.props;

        const relevantStyles = this.relevantStyles(
            style_cell,
            style_data,
            style_cell_conditional,
            style_data_conditional
        );

        const partialCellStyles = this.dataPartialStyles(
            visibleColumns,
            relevantStyles,
            virtualized.data,
            virtualized.offset
        );

        const cellStyles = this.dataStyles(
            partialCellStyles,
            visibleColumns,
            relevantStyles,
            virtualized.data,
            virtualized.offset,
            active_cell,
            selected_cells
        );

        const dataOpStyles = this.dataOpStyles(
            (row_selectable ? 1 : 0) + (row_deletable ? 1 : 0),
            relevantStyles,
            virtualized.data,
            virtualized.offset
        );

        const dropdowns = this.cellDropdowns(
            visibleColumns,
            virtualized.data,
            virtualized.indices,
            dropdown_conditional,
            dropdown,
            dropdown_data
        );

        const operations = this.cellOperations(
            id,
            data,
            virtualized.data,
            virtualized.indices,
            row_selectable,
            row_deletable,
            selected_rows,
            setProps
        );

        const partialCellWrappers = this.cellWrappers.partialGet(
            visibleColumns,
            virtualized.data,
            virtualized.offset
        );

        const cellWrappers = this.cellWrappers.get(
            partialCellWrappers,
            virtualized.offset,
            active_cell,
            selected_cells
        );

        const markdown = this.getMarkdown(markdown_options);

        const partialCellContents = this.cellContents.partialGet(
            visibleColumns,
            virtualized.data,
            virtualized.offset,
            !!is_focused,
            dropdowns,
            loading_state,
            markdown
        );

        const cellContents = this.cellContents.get(
            partialCellContents,
            active_cell,
            applyFocus || false,
            visibleColumns,
            virtualized.data,
            virtualized.offset,
            !!is_focused,
            dropdowns,
            loading_state,
            markdown
        );

        const ops = this.getDataOpCells(operations, dataOpStyles, dataOpEdges);

        const cells = this.getDataCells(
            cellWrappers,
            cellContents,
            cellStyles,
            dataEdges
        );

        return this.getCells(ops, cells);
    }

    getCells = memoizeOne(
        (opCells: JSX.Element[][], dataCells: JSX.Element[][]) =>
            arrayMap2(opCells, dataCells, (o, c) =>
                o.length ? o.concat(c) : c
            )
    );

    getDataOpCell = memoizerCache<[number, number]>()(
        (
            operation: JSX.Element,
            style: CSSProperties | undefined,
            borderBottom: any,
            borderLeft: any,
            borderRight: any,
            borderTop: any
        ) => {
            return React.cloneElement(operation, {
                style: R.mergeAll([
                    {borderBottom, borderLeft, borderRight, borderTop},
                    style,
                    operation.props.style
                ])
            });
        }
    );

    getDataOpCells = memoizeOne(
        (
            ops: JSX.Element[][],
            styles: (CSSProperties | undefined)[][],
            edges: IEdgesMatrices | undefined
        ) =>
            matrixMap2(ops, styles, (o, s, i, j) => {
                const edge = edges && edges.getStyle(i, j);

                return this.getDataOpCell.get(i, j)(
                    o,
                    s,
                    edge && edge.borderBottom,
                    edge && edge.borderLeft,
                    edge && edge.borderRight,
                    edge && edge.borderTop
                );
            })
    );

    getDataCell = memoizerCache<[number, number]>()(
        (
            wrapper: JSX.Element,
            content: JSX.Element | undefined,
            style: CSSProperties | undefined,
            borderBottom: any,
            borderLeft: any,
            borderRight: any,
            borderTop: any
        ) => {
            return React.cloneElement(wrapper, {
                children: [content],
                style: R.mergeRight(style || {}, {
                    borderBottom,
                    borderLeft,
                    borderRight,
                    borderTop
                } as any)
            });
        }
    );

    getDataCells = memoizeOne(
        (
            wrappers: JSX.Element[][],
            contents: JSX.Element[][],
            styles: (CSSProperties | undefined)[][],
            edges: IEdgesMatrices | undefined
        ) =>
            matrixMap3(wrappers, styles, contents, (w, s, c, i, j) => {
                const edge = edges && edges.getStyle(i, j);

                return this.getDataCell.get(i, j)(
                    w,
                    c,
                    s,
                    edge && edge.borderBottom,
                    edge && edge.borderLeft,
                    edge && edge.borderRight,
                    edge && edge.borderTop
                );
            })
    );
}
