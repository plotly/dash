import * as R from 'ramda';

const styles = {
    scroll: {
        row: (props) => {
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
                style.left = R.sum(R.pluck(
                    'width',
                    R.slice(0, column_index, props.columns)
                ));
                style.top = 'auto';
                style.overflowY = 'hidden';
                style.height = 35;
                style.width = props.columns[column_index].width;
                style.maxWidth = props.columns[column_index].width;
                style.minWidth = props.columns[column_index].width;
            }

            return style;
        },

        containerDiv: (props) => {
            const style = {};

            if (props.n_fixed_columns) {
                style.overflowX = 'scroll';
                style.width = props.width;
                style.marginLeft = R.sum(R.pluck(
                    'width',
                    R.slice(0, props.n_fixed_columns, props.columns)
                ));
            }

            return style;
        },

        table: (props, column_index) => {
            const style = {};

            if (props.n_fixed_columns) {
                style.overflowX = 'scroll';
            }

            return style;
        },
    }
}

export default styles;
