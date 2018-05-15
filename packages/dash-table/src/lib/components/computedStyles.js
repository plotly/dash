import * as R from 'ramda';

const HEIGHT = 35;

const styles = {
    scroll: {
        row: props => {
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
                style.marginLeft =
                    R.sum(
                        R.pluck(
                            'width',
                            R.slice(0, props.n_fixed_columns, props.columns)
                        )
                    ) - 1; /* taking into account some border somewhere */
            }

            if (props.n_fixed_rows) {
                style.overflowY = 'scroll';
                style.height = props.height;
                style.marginTop = HEIGHT * props.n_fixed_rows;
            }

            return style;
        },

        table: (props, column_index) => {
            const style = {};

            return style;
        },
    },
};

export default styles;
