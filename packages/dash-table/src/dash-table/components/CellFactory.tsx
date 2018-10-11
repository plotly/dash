import React from 'react';

import { ICellFactoryOptions } from 'dash-table/components/Table/props';
import derivedCellWrappers from 'dash-table/derived/cell/wrappers';
import derivedCellInputs from 'dash-table/derived/cell/inputs';
import derivedCellOperations from 'dash-table/derived/cell/operations';
import derivedCellStyles from 'dash-table/derived/cell/wrapperStyles';
import derivedDropdowns from 'dash-table/derived/cell/dropdowns';

import { matrixMap3 } from 'core/math/matrixZipMap';
import { arrayMap } from 'core/math/arrayZipMap';

export default class CellFactory {
    private readonly cellInputs = derivedCellInputs();
    private readonly cellOperations = derivedCellOperations();
    private readonly cellDropdowns = derivedDropdowns();

    private get props() {
        return this.propsFn();
    }

    constructor(
        private readonly propsFn: () => ICellFactoryOptions,
        private readonly cellStyles = derivedCellStyles(propsFn().id),
        private readonly cellWrappers = derivedCellWrappers(propsFn().id)
    ) { }

    public createCells() {
        const {
            active_cell,
            columns,
            column_conditional_dropdowns,
            column_conditional_styles,
            column_static_dropdown,
            column_static_style,
            dataframe,
            dropdown_properties, // legacy
            editable,
            id,
            is_focused,
            row_deletable,
            row_selectable,
            selected_cell,
            selected_rows,
            setProps,
            viewport
        } = this.props;

        const operations = this.cellOperations(
            active_cell,
            dataframe,
            viewport.dataframe,
            viewport.indices,
            row_selectable,
            row_deletable,
            selected_rows,
            setProps
        );

        const wrappers = this.cellWrappers(
            active_cell,
            columns,
            viewport.dataframe,
            editable,
            selected_cell
        );

        const wrapperStyles = this.cellStyles(
            columns,
            column_conditional_styles,
            column_static_style,
            viewport.dataframe
        );

        const dropdowns = this.cellDropdowns(id)(
            columns,
            viewport.dataframe,
            viewport.indices,
            column_conditional_dropdowns,
            column_static_dropdown,
            dropdown_properties
        );

        const inputs = this.cellInputs(
            active_cell,
            columns,
            viewport.dataframe,
            editable,
            !!is_focused,
            id,
            dropdowns,
            this.propsFn
        );

        const cells = matrixMap3(
            wrappers,
            wrapperStyles,
            inputs,
            (w, s, i) => React.cloneElement(w, { children: [i], style: s })
        );

        return arrayMap(
            operations,
            cells,
            (o, c) => Array.prototype.concat(o, c)
        );
    }
}