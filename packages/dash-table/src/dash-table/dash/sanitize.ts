
import * as R from 'ramda';

import { memoizeOne } from 'core/memoizer';
import { Columns, ColumnType, INumberLocale } from 'dash-table/components/Table/props';

const D3_DEFAULT_LOCALE: INumberLocale = {
    symbol: ['$', ''],
    decimal: '.',
    group: ',',
    grouping: [3],
    percent: '%',
    separate_4digits: true
};

const DEFAULT_NULLY = '';
const DEFAULT_SPECIFIER = '';

const applyDefaultToLocale = memoizeOne((locale: INumberLocale) => getLocale(locale));

const applyDefaultsToColumns = memoizeOne(
    (defaultLocale: INumberLocale, columns: Columns) => R.map(column => {
        const c = R.clone(column);

        if (c.type === ColumnType.Numeric && c.format) {
            c.format.locale = getLocale(defaultLocale, c.format.locale);
            c.format.nully = getNully(c.format.nully);
            c.format.specifier = getSpecifier(c.format.specifier);
        }
        return c;
    }, columns)
);

export default (props: any) => {
    const locale_format = applyDefaultToLocale(props.locale_format);

    return R.mergeAll([
        props,
        {
            columns: applyDefaultsToColumns(locale_format, props.columns),
            locale_format
        }
    ]);
};

export const getLocale = (...locales: Partial<INumberLocale>[]): INumberLocale =>
    R.mergeAll([
        D3_DEFAULT_LOCALE,
        ...locales
    ]) as INumberLocale;

export const getSpecifier = (specifier?: string) => specifier === undefined ?
    DEFAULT_SPECIFIER :
    specifier;

export const getNully = (nully?: any) => nully === undefined ?
    DEFAULT_NULLY :
    nully;