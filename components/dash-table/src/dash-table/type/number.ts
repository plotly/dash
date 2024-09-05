import * as R from 'ramda';
import {formatLocale} from 'd3-format';
import isNumeric from 'fast-isnumeric';

import {
    INumberColumn,
    INumberLocale,
    NumberFormat
} from 'dash-table/components/Table/props';
import {reconcileNull, isNully} from './null';
import {IReconciliation} from './reconcile';

const convertToD3 = ({group, symbol, ...others}: INumberLocale) => ({
    currency: symbol,
    thousands: group,
    ...R.omit(['separate_4digits', 'symbol'], others)
});

export function coerce(
    value: any,
    options: INumberColumn | undefined
): IReconciliation {
    return isNumeric(value)
        ? {success: true, value: +value}
        : reconcileNull(value, options);
}

export function getFormatter(format: NumberFormat) {
    if (!format) {
        return (value: any) => value;
    }

    const locale = formatLocale(convertToD3(format.locale));

    const numberFormatter = format.prefix
        ? locale.formatPrefix(format.specifier, format.prefix)
        : locale.format(format.specifier);

    const thousandsSpecifier = format.locale.separate_4digits
        ? format.specifier
        : format.specifier.replace(/,/, '');

    const thousandsFormatter = format.prefix
        ? locale.formatPrefix(thousandsSpecifier, format.prefix)
        : locale.format(thousandsSpecifier);

    return (value: any) => {
        value = isNully(value) ? format.nully : value;

        return typeof value !== 'number'
            ? value
            : Math.abs(value) < 10000
            ? thousandsFormatter(value)
            : numberFormatter(value);
    };
}

export function validate(
    value: any,
    options: INumberColumn | undefined
): IReconciliation {
    return typeof value === 'number' && !isNully(value)
        ? {success: true, value}
        : reconcileNull(value, options);
}
