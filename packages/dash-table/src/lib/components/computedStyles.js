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

        borderStyle: (args) => {
            const {
                i: ci,
                idx: ri,
                columns,
                selected_cell,
                dataframe,
                collapsable,
                expanded_rows,
                active_cell,
                row_selectable
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
            const selectedRows = sortNumerical(R.uniq(R.pluck(0, selected_cell)));
            const selectedCols = sortNumerical(R.uniq(R.pluck(1, selected_cell)));

            const showInsideLeftEdge = isActive
                ? true
                : ci === R.head(selectedCols) &&
                  !row_selectable &&
                  R.contains(ri, selectedRows);
            const showInsideTopEdge = isActive
                ? true
                : ri === R.head(selectedRows) && R.contains(ci, selectedCols);
            const showInsideRightEdge = isActive
                ? true
                : ci === R.last(selectedCols) && R.contains(ri, selectedRows);
            const showBottomEdge = isActive
                ? true
                : (ri === R.last(selectedRows) || false) &&
                  R.contains(ci, selectedCols);

            const isRightmost = ci === R.last(vci);
            const isLeftmost = row_selectable
                ? ci === -1  // -1 refers to meta columns like the row-select checkbox column
                : ci === R.head(vci);
            const isTopmost = ri === 0;
            const isBottommost = ri === dataframe.length - 1;
            const isNeighborToExpanded =
                collapsable && R.contains(ri, expanded_rows) && ci === vci[0];
            const isAboveExpanded = collapsable && R.contains(ri, expanded_rows);
            const isSelectedColumn = R.contains(ci, selectedCols);
            const isSelectedRow = R.contains(ri, selectedRows);

            // rules are applied in the order that they are supplied
            const boxShadowRules = [
                showInsideLeftEdge || isNeighborToExpanded
                    ? doLeft(ACCENT, isActive ? 2 : 1)
                    : null,
                showInsideTopEdge ? doTop(ACCENT, isActive ? 2 : 1) : null,
                showBottomEdge ? doBottom(ACCENT, isActive ? 2 : 1) : null,
                showInsideRightEdge ? doRight(ACCENT, isActive ? 2 : 1) : null,
                isSelectedColumn && isTopmost ? doTop(ACCENT, 1) : null,
                isSelectedRow && isLeftmost ? doLeft(ACCENT, 1) : null,

                doLeft(BORDER, 1),
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

            return style;
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
