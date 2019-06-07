import * as R from 'ramda';
import React from 'react';

import { matrixMap2, matrixMap3 } from 'core/math/matrixZipMap';
import { arrayMap2 } from 'core/math/arrayZipMap';

import { ICellFactoryProps } from 'dash-table/components/Table/props';
import derivedCellWrappers from 'dash-table/derived/cell/wrappers';
import derivedCellContents from 'dash-table/derived/cell/contents';
import derivedCellOperations from 'dash-table/derived/cell/operations';
import derivedCellStyles, { derivedDataOpStyles } from 'dash-table/derived/cell/wrapperStyles';
import derivedDropdowns from 'dash-table/derived/cell/dropdowns';
import { derivedRelevantCellStyles } from 'dash-table/derived/style';
import { IEdgesMatrices } from 'dash-table/derived/edges/type';

export default class CellFactory {

    private get props() {
        return this.propsFn();
    }

    constructor(
        private readonly propsFn: () => ICellFactoryProps,
        private readonly cellContents = derivedCellContents(propsFn),
        private readonly cellDropdowns = derivedDropdowns(),
        private readonly cellOperations = derivedCellOperations(),
        private readonly cellStyles = derivedCellStyles(),
        private readonly dataOpStyles = derivedDataOpStyles(),
        private readonly cellWrappers = derivedCellWrappers(propsFn),
        private readonly relevantStyles = derivedRelevantCellStyles()
    ) { }

    public createCells(dataEdges: IEdgesMatrices | undefined, dataOpEdges: IEdgesMatrices | undefined) {
        const {
            active_cell,
            columns,
            dropdown_conditional,
            dropdown,
            data,
            dropdown_data,
            editable,
            is_focused,
            row_deletable,
            row_selectable,
            selected_cells,
            selected_rows,
            setProps,
            style_cell,
            style_cell_conditional,
            style_data,
            style_data_conditional,
            virtualized
        } = this.props;

        const relevantStyles = this.relevantStyles(
            style_cell,
            style_data,
            style_cell_conditional,
            style_data_conditional
        );

        const cellStyles = this.cellStyles(
            columns,
            relevantStyles,
            virtualized.data,
            virtualized.offset,
            selected_cells
        );

        const dataOpStyles = this.dataOpStyles(
            (row_selectable ? 1 : 0) + (row_deletable ? 1 : 0),
            relevantStyles,
            virtualized.data,
            virtualized.offset
        );

        const dropdowns = this.cellDropdowns(
            columns,
            virtualized.data,
            virtualized.indices,
            dropdown_conditional,
            dropdown,
            dropdown_data
        );

        const operations = this.cellOperations(
            data,
            virtualized.data,
            virtualized.indices,
            row_selectable,
            row_deletable,
            selected_rows,
            setProps
        );

        const cellWrappers = this.cellWrappers(
            active_cell,
            columns,
            virtualized.data,
            virtualized.offset,
            selected_cells
        );

        const cellContents = this.cellContents(
            active_cell,
            columns,
            virtualized.data,
            virtualized.offset,
            editable,
            !!is_focused,
            dropdowns
        );

        const ops = matrixMap2(
            operations,
            dataOpStyles,
            (o, s, i, j) => React.cloneElement(o, {
                style: R.mergeAll([
                    dataOpEdges && dataOpEdges.getStyle(i, j),
                    s,
                    o.props.style
                ])
            })
        );

        const cells = matrixMap3(
            cellWrappers,
            cellStyles,
            cellContents,
            (w, s, c, i, j) => React.cloneElement(w, {
                children: [c],
                style: R.mergeAll([
                    s,
                    dataEdges && dataEdges.getStyle(i, j)
                ])
            })
        );

        return arrayMap2(
            ops,
            cells,
            (o, c) => Array.prototype.concat(o, c)
        );
    }
}
