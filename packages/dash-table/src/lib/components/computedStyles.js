import React from 'react';
import * as R from 'ramda';

const HEIGHT = 35;

const styles = {
    scroll: {
        row2: props => {
            const style = {};

            if (props.n_fixed_columns) {
                style.position = 'relative';
            }

            return style;
        },

        cell: (props, column_index) => {
            const style = {};

            if (props.n_fixed_columns && column_index < props.n_fixed_columns) {
                style.position = 'absolute';
                style.left = R.sum(
                    R.pluck('width', R.slice(0, column_index, props.columns))
                );
                style.top = 'auto';
                style.overflowY = 'hidden';
                style.height = 35;
                style.width = props.columns[column_index].width;
                style.maxWidth = props.columns[column_index].width;
                style.minWidth = props.columns[column_index].width;
            }

            if (props.n_fixed_rows) {
                style.width = props.columns[column_index].width;
                style.maxWidth = props.columns[column_index].width;
                style.minWidth = props.columns[column_index].width;
            }

            return style;
        },

        borderStyle: args => {
            const {
                i: ci,
                idx: ri,
                columns,
                selected_cell,
                dataframe,
                collapsable,
                expanded_rows,
                active_cell,
                row_deletable,
                row_selectable,
                style_as_list_view,
            } = args;

            // visible col indices
            const vci = [];
            columns.forEach((c, i) => {
                if (!c.hidden) {
                    vci.push(i);
                }
            });

            const isActive = active_cell[0] === ri && active_cell[1] === ci;

            // Left, Right, Top, Bottom
            const ACCENT = 'var(--accent)';
            const BORDER = 'var(--border)';

            const doLeft = (c, t) => `inset ${t}px 0px 0px 0px ${c}`;
            const doRight = (c, t) => `inset -${t}px 0px 0px 0px ${c}`;
            const doTop = (c, t) => `inset 0px ${t}px 0px 0px ${c}`;
            const doBottom = (c, t) => `inset 0px -${t}px 0px 0px ${c}`;

            const sortNumerical = R.sort((a, b) => a - b);
            const selectedRows = sortNumerical(
                R.uniq(R.pluck(0, selected_cell))
            );
            const selectedCols = sortNumerical(
                R.uniq(R.pluck(1, selected_cell))
            );
            const firstCol = R.head(selectedCols);
            const lastCol = R.last(selectedCols);
            const firstRow = R.head(selectedRows);
            const lastRow = R.last(selectedRows);

            const isWithinRowSelections = R.contains(ri, selectedRows);
            const isWithinColSelections = R.contains(ci, selectedCols);

            let showLeftEdge = isActive;
            let showTopEdge = isActive;
            const showInsideRightEdge = isActive;
            const showInsideBottomEdge = isActive;

            if (
                (active_cell[0] === ri && active_cell[1] + 1 === ci) ||
                (isWithinRowSelections &&
                    (firstCol === ci || lastCol + 1 === ci))
            ) {
                showLeftEdge = true;
            }
            if (
                (active_cell[0] + 1 === ri && active_cell[1] === ci) ||
                (isWithinColSelections &&
                    (firstRow === ri || lastRow + 1 === ri))
            ) {
                showTopEdge = true;
            }

            const isRightmost = ci === R.last(vci);

            // -1 refers to meta columns like the row-select checkbox column
            // TODO - Get row-select and row-delete to work together
            const isLeftmost = ((row_selectable || row_deletable) ?
                ci === -1 : ci === R.head(vci));
            const isTopmost = ri === 0;
            const isBottommost = ri === dataframe.length - 1;
            const isNeighborToExpanded =
                collapsable && R.contains(ri, expanded_rows) && ci === vci[0];
            const isAboveExpanded =
                collapsable && R.contains(ri, expanded_rows);

            let leftEdgeThickness = 1;
            if (isActive && !isLeftmost) {
                leftEdgeThickness = 2;
            }

            let topEdgeThickness = 1;
            if (isActive && !isTopmost) {
                topEdgeThickness = 2;
            }

            // rules are applied in the order that they are supplied
            const boxShadowRules = [
                showLeftEdge || isNeighborToExpanded
                    ? doLeft(ACCENT, leftEdgeThickness)
                    : null,
                showTopEdge ? doTop(ACCENT, topEdgeThickness) : null,
                showInsideBottomEdge ? doBottom(ACCENT, 1) : null,
                showInsideRightEdge ? doRight(ACCENT, 1) : null,
                isWithinColSelections && isTopmost ? doTop(ACCENT, 1) : null,
                isWithinRowSelections && isLeftmost ? doLeft(ACCENT, 1) : null,
                !style_as_list_view || ci === -1 ? doLeft(BORDER, 1) : null,
                doTop(BORDER, 1),

                isBottommost || isAboveExpanded ? doBottom(BORDER, 1) : null,
                isRightmost ? doRight(BORDER, 1) : null,
            ].filter(R.complement(R.not));

            const sortedBoxRules = R.sort(
                a => (R.contains(ACCENT, a) ? -1 : 1),
                boxShadowRules
            );

            const style = {
                boxShadow: `${sortedBoxRules.join(', ')}`,
            };

            let borderFixDiv = null;
            if (
                (ci === lastCol + 1 && ri === lastRow + 1) ||
                (active_cell[0] + 1 === ri && active_cell[1] + 1 === ci)
            ) {
                borderFixDiv = (
                    <div
                        className={`selected-square selected-square-bottom-right`}
                    />
                );
            }

            return {style, borderFixDiv};
        },

        row: (props, row_index) => {
            const style = {};
            if (props.n_fixed_rows && row_index < props.n_fixed_rows) {
                style.position = 'absolute';
                style.top = HEIGHT * row_index;
                style.left = 0;
                style.overflowX = 'hidden';
            }
            return style;
        },

        containerDiv: props => {
            const style = {};

            if (props.n_fixed_columns) {
                style.overflowX = 'scroll';
                style.width = props.width;

                // taking into account some border somewhere
                const BORDER_FIX = -1;
                style.marginLeft =
                    R.sum(
                        R.pluck(
                            'width',
                            R.slice(0, props.n_fixed_columns, props.columns)
                        )
                    ) + BORDER_FIX;
            }

            if (props.n_fixed_rows) {
                style.overflowY = 'scroll';
                style.height = props.height;
                style.marginTop = HEIGHT * props.n_fixed_rows;
            }

            return style;
        },

        table: () => {
            const style = {};

            return style;
        },
    },
};

export default styles;
