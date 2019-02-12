import React from 'react';

import { ICellFactoryProps } from 'dash-table/components/Table/props';
import derivedCellWrappers from 'dash-table/derived/cell/wrappers';
import derivedCellContents from 'dash-table/derived/cell/contents';
import derivedCellOperations from 'dash-table/derived/cell/operations';
import derivedCellStyles from 'dash-table/derived/cell/wrapperStyles';
import derivedDropdowns from 'dash-table/derived/cell/dropdowns';
import { derivedRelevantCellStyles } from 'dash-table/derived/style';

import { matrixMap3 } from 'core/math/matrixZipMap';
import { arrayMap } from 'core/math/arrayZipMap';

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
        private readonly cellWrappers = derivedCellWrappers(propsFn),
        private readonly relevantStyles = derivedRelevantCellStyles()
    ) { }

    public createCells() {
        const {
            active_cell,
            columns,
            column_conditional_dropdowns,
            column_static_dropdown,
            data,
            dropdown_properties, // legacy
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

        const operations = this.cellOperations(
            active_cell,
            data,
            virtualized.data,
            virtualized.indices,
            row_selectable,
            row_deletable,
            selected_rows,
            setProps
        );

        const relevantStyles = this.relevantStyles(
            style_cell,
            style_data,
            style_cell_conditional,
            style_data_conditional
        );

        const wrapperStyles = this.cellStyles(
            columns,
            relevantStyles,
            virtualized.data,
            virtualized.offset
        );

        const dropdowns = this.cellDropdowns(
            columns,
            virtualized.data,
            virtualized.indices,
            column_conditional_dropdowns,
            column_static_dropdown,
            dropdown_properties
        );

        const wrappers = this.cellWrappers(
            active_cell,
            columns,
            virtualized.data,
            virtualized.offset,
            selected_cells
        );

        const contents = this.cellContents(
            active_cell,
            columns,
            virtualized.data,
            virtualized.offset,
            editable,
            !!is_focused,
            dropdowns
        );

        const cells = matrixMap3(
            wrappers,
            wrapperStyles,
            contents,
            (w, s, c) => React.cloneElement(w, { children: [c], style: s })
        );

        return arrayMap(
            operations,
            cells,
            (o, c) => Array.prototype.concat(o, c)
        );
    }
}