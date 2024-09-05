import {ColumnType, IColumnType} from 'dash-table/components/Table/props';

import {getFormatter as getNumberFormatter} from './number';

const DEFAULT_FORMATTER = (value: any) => value;
export default (c: IColumnType) => {
    let formatter;
    switch (c.type) {
        case ColumnType.Numeric:
            formatter = getNumberFormatter(c.format);
            break;
    }

    return formatter || DEFAULT_FORMATTER;
};
