import {memoizeOne} from 'core/memoizer';

import {
    derivedPartialDataEdges,
    derivedDataEdges
} from 'dash-table/derived/edges/data';
import derivedDataOpEdges from 'dash-table/derived/edges/operationOfData';
import derivedFilterEdges from 'dash-table/derived/edges/filter';
import derivedFilterOpEdges from 'dash-table/derived/edges/operationOfFilters';
import derivedHeaderEdges from 'dash-table/derived/edges/header';
import derivedHeaderOpEdges from 'dash-table/derived/edges/operationOfHeaders';
import {EdgesMatrices, IEdgesMatrices} from 'dash-table/derived/edges/type';

import getHeaderRows from 'dash-table/derived/header/headerRows';

import {
    derivedRelevantCellStyles,
    derivedRelevantFilterStyles,
    derivedRelevantHeaderStyles
} from 'dash-table/derived/style';
import {
    Style,
    Cells,
    DataCells,
    BasicFilters,
    Headers
} from 'dash-table/derived/style/props';

import {
    ControlledTableProps,
    Columns,
    IViewportOffset,
    Data,
    ICellCoordinates,
    TableAction,
    SelectedCells
} from './Table/props';
import {SingleColumnSyntaxTree} from 'dash-table/syntax-tree';

type EdgesMatricesOp = EdgesMatrices | undefined;

export default class EdgeFactory {
    private readonly dataStyles = derivedRelevantCellStyles();
    private readonly filterStyles = derivedRelevantFilterStyles();
    private readonly headerStyles = derivedRelevantHeaderStyles();

    private readonly getPartialDataEdges = derivedPartialDataEdges();
    private readonly getDataEdges = derivedDataEdges();
    private readonly getDataOpEdges = derivedDataOpEdges();
    private readonly getFilterEdges = derivedFilterEdges();
    private readonly getFilterOpEdges = derivedFilterOpEdges();
    private readonly getHeaderEdges = derivedHeaderEdges();
    private readonly getHeaderOpEdges = derivedHeaderOpEdges();

    private static clone(target: EdgesMatricesOp) {
        return target && target.clone();
    }

    private static hasPrecedence(
        target: number,
        other: number,
        cutoff: number
    ): boolean {
        return (other <= cutoff || target === Infinity) && other <= target;
    }

    private hOverride(
        previous: EdgesMatricesOp,
        target: EdgesMatricesOp,
        cutoffWeight: number
    ) {
        if (!previous || !target) {
            return;
        }

        const hPrevious = previous.getMatrices().horizontal;
        const hTarget = target.getMatrices().horizontal;

        const iPrevious = hPrevious.rows - 1;
        const iTarget = 0;

        for (let j = 0; j < hPrevious.columns; j++) {
            if (
                EdgeFactory.hasPrecedence(
                    hPrevious.getWeight(iPrevious, j),
                    hTarget.getWeight(iTarget, j),
                    cutoffWeight
                )
            ) {
                hTarget.setEdge(
                    iTarget,
                    j,
                    hPrevious.getEdge(iPrevious, j),
                    Infinity,
                    true
                );
            }
            hPrevious.setEdge(iPrevious, j, 'none', -Infinity, true);
        }
    }

    private vOverride(
        previous: EdgesMatricesOp,
        target: EdgesMatricesOp,
        cutoffWeight: number
    ) {
        if (!previous || !target) {
            return;
        }

        const hPrevious = previous.getMatrices().vertical;
        const hTarget = target.getMatrices().vertical;

        const jPrevious = hPrevious.columns - 1;
        const jTarget = 0;

        for (let i = 0; i < hPrevious.rows; i++) {
            if (
                EdgeFactory.hasPrecedence(
                    hPrevious.getWeight(i, jPrevious),
                    hTarget.getWeight(i, jTarget),
                    cutoffWeight
                )
            ) {
                hTarget.setEdge(
                    i,
                    jTarget,
                    hPrevious.getEdge(i, jPrevious),
                    Infinity,
                    true
                );
            }
            hPrevious.setEdge(i, jPrevious, 'none', -Infinity, true);
        }
    }

    private hReconcile(
        target: EdgesMatrices | undefined,
        next: EdgesMatrices | undefined,
        cutoffWeight: number
    ) {
        if (!target || !next) {
            return;
        }

        const hNext = next.getMatrices().horizontal;
        const hTarget = target.getMatrices().horizontal;

        const iNext = 0;
        const iTarget = hTarget.rows - 1;

        if (!isFinite(iTarget)) {
            return;
        }

        for (let j = 0; j < hTarget.columns; j++) {
            if (
                !EdgeFactory.hasPrecedence(
                    hTarget.getWeight(iTarget, j),
                    hNext.getWeight(iNext, j),
                    cutoffWeight
                )
            ) {
                hTarget.setEdge(iTarget, j, 'none', -Infinity, true);
            }
        }
    }

    private vReconcile(
        target: EdgesMatrices | undefined,
        next: EdgesMatrices | undefined,
        cutoffWeight: number
    ) {
        if (!target || !next) {
            return;
        }

        const vNext = next.getMatrices().vertical;
        const vTarget = target.getMatrices().vertical;

        const jNext = 0;
        const jTarget = vTarget.columns - 1;

        for (let i = 0; i < vTarget.rows; i++) {
            if (
                !EdgeFactory.hasPrecedence(
                    vTarget.getWeight(i, jTarget),
                    vNext.getWeight(i, jNext),
                    cutoffWeight
                )
            ) {
                vTarget.setEdge(i, jTarget, 'none', -Infinity, true);
            }
        }
    }

    private get props() {
        return this.propsFn();
    }

    constructor(private readonly propsFn: () => ControlledTableProps) {}

    public createEdges() {
        const {
            active_cell,
            columns,
            filter_action,
            workFilter,
            fixed_columns,
            fixed_rows,
            row_deletable,
            row_selectable,
            selected_cells,
            style_as_list_view,
            style_cell,
            style_cell_conditional,
            style_data,
            style_data_conditional,
            style_filter,
            style_filter_conditional,
            style_header,
            style_header_conditional,
            virtualized,
            visibleColumns
        } = this.props;

        return this.memoizedCreateEdges(
            active_cell,
            columns,
            visibleColumns,
            (row_deletable ? 1 : 0) + (row_selectable ? 1 : 0),
            filter_action.type !== TableAction.None,
            workFilter.map,
            fixed_columns,
            fixed_rows,
            selected_cells,
            style_as_list_view,
            style_cell,
            style_cell_conditional,
            style_data,
            style_data_conditional,
            style_filter,
            style_filter_conditional,
            style_header,
            style_header_conditional,
            virtualized.data,
            virtualized.offset
        );
    }

    private memoizedCreateEdges = memoizeOne(
        (
            active_cell: ICellCoordinates | undefined,
            columns: Columns,
            visibleColumns: Columns,
            operations: number,
            filter_action: boolean,
            filterMap: Map<string, SingleColumnSyntaxTree>,
            fixed_columns: number,
            fixed_rows: number,
            selected_cells: SelectedCells,
            style_as_list_view: boolean,
            style_cell: Style,
            style_cell_conditional: Cells,
            style_data: Style,
            style_data_conditional: DataCells,
            style_filter: Style,
            style_filter_conditional: BasicFilters,
            style_header: Style,
            style_header_conditional: Headers,
            virtualizedData: Data,
            offset: IViewportOffset
        ) => {
            const dataStyles = this.dataStyles(
                style_cell,
                style_data,
                style_cell_conditional,
                style_data_conditional
            );

            const filterStyles = this.filterStyles(
                style_cell,
                style_filter,
                style_cell_conditional,
                style_filter_conditional
            );

            const headerStyles = this.headerStyles(
                style_cell,
                style_header,
                style_cell_conditional,
                style_header_conditional
            );

            const headerRows = getHeaderRows(columns);

            const partialDataEdges = this.getPartialDataEdges(
                visibleColumns,
                dataStyles,
                virtualizedData,
                offset,
                style_as_list_view
            );

            let dataEdges = this.getDataEdges(
                partialDataEdges,
                visibleColumns,
                dataStyles,
                virtualizedData,
                offset,
                active_cell,
                selected_cells
            );

            let dataOpEdges = this.getDataOpEdges(
                operations,
                dataStyles,
                virtualizedData,
                offset,
                style_as_list_view
            );

            let filterEdges = this.getFilterEdges(
                visibleColumns,
                filter_action,
                filterMap,
                filterStyles,
                style_as_list_view
            );

            let filterOpEdges = this.getFilterOpEdges(
                operations,
                filter_action,
                filterStyles,
                style_as_list_view
            );

            let headerEdges = this.getHeaderEdges(
                visibleColumns,
                headerRows,
                headerStyles,
                style_as_list_view
            );

            let headerOpEdges = this.getHeaderOpEdges(
                operations,
                headerRows,
                headerStyles,
                style_as_list_view
            );

            const cutoffWeight =
                (style_cell ? 1 : 0) + style_cell_conditional.length - 1;

            headerEdges = EdgeFactory.clone(headerEdges);
            headerOpEdges = EdgeFactory.clone(headerOpEdges);
            filterEdges = EdgeFactory.clone(filterEdges);
            filterOpEdges = EdgeFactory.clone(filterOpEdges);
            dataEdges = EdgeFactory.clone(dataEdges);
            dataOpEdges = EdgeFactory.clone(dataOpEdges);

            this.hReconcile(
                headerEdges,
                filterEdges || dataEdges,
                cutoffWeight
            );
            this.hReconcile(
                headerOpEdges,
                filterOpEdges || dataOpEdges,
                cutoffWeight
            );
            this.hReconcile(filterEdges, dataEdges, cutoffWeight);
            this.hReconcile(filterOpEdges, dataOpEdges, cutoffWeight);

            this.vReconcile(headerOpEdges, headerEdges, cutoffWeight);
            this.vReconcile(filterOpEdges, filterEdges, cutoffWeight);
            this.vReconcile(dataOpEdges, dataEdges, cutoffWeight);

            if (fixed_rows === headerRows) {
                if (filter_action) {
                    this.hOverride(headerEdges, filterEdges, cutoffWeight);
                    this.hOverride(headerOpEdges, filterOpEdges, cutoffWeight);
                } else {
                    this.hOverride(headerEdges, dataEdges, cutoffWeight);
                    this.hOverride(headerOpEdges, dataOpEdges, cutoffWeight);
                }
            } else if (filter_action && fixed_rows === headerRows + 1) {
                this.hOverride(filterEdges, dataEdges, cutoffWeight);
                this.hOverride(filterOpEdges, dataOpEdges, cutoffWeight);
            }

            if (fixed_columns === operations) {
                this.vOverride(headerOpEdges, headerEdges, cutoffWeight);
                this.vOverride(filterOpEdges, filterEdges, cutoffWeight);
                this.vOverride(dataOpEdges, dataEdges, cutoffWeight);
            }

            return {
                dataEdges: dataEdges as IEdgesMatrices | undefined,
                dataOpEdges: dataOpEdges as IEdgesMatrices | undefined,
                filterEdges: filterEdges as IEdgesMatrices | undefined,
                filterOpEdges: filterOpEdges as IEdgesMatrices | undefined,
                headerEdges: headerEdges as IEdgesMatrices | undefined,
                headerOpEdges: headerOpEdges as IEdgesMatrices | undefined
            };
        }
    );
}
