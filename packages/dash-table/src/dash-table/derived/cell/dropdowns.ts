import * as R from 'ramda';

import { memoizeOneFactory } from 'core/memoizer';

import {
    Data,
    Datum,
    VisibleColumns,
    ColumnId,
    Indices,
    IColumnDropdown,
    IConditionalColumnDropdown,
    IDropdownProperties
} from 'dash-table/components/Table/props';
import SyntaxTree from 'core/syntax-tree';
import memoizerCache from 'core/memoizerCache';

interface IDropdownOption {
    label: string;
    value: string;
}

type IDropdownOptions = IDropdownOption[];

interface IConditionalDropdown {
    condition: string;
    dropdown: IDropdownOptions;
}

const mapData = R.addIndex<Datum, JSX.Element[]>(R.map);

const getDropdown = (
    astCache: (key: [ColumnId, number], query: string) => SyntaxTree,
    conditionalDropdowns: any,
    datum: Datum,
    property: ColumnId,
    staticDropdown: any
) => {
    const dropdowns = [
        ...(staticDropdown ? [staticDropdown] : []),
        ...R.map(
            ([cd]) => cd.dropdown,
            R.filter(
                ([cd, i]) => astCache([property, i], cd.condition).evaluate(datum),
                R.addIndex<IConditionalDropdown, [IConditionalDropdown, number]>(R.map)(
                    (cd, i) => [cd, i],
                    conditionalDropdowns
                ))
        )
    ];

    return dropdowns.length ? dropdowns.slice(-1)[0] : undefined;
};

const getter = (
    astCache: (key: [ColumnId, number], query: string) => SyntaxTree,
    columns: VisibleColumns,
    data: Data,
    indices: Indices,
    columnConditionalDropdown: IConditionalColumnDropdown[],
    columnStaticDropdown: IColumnDropdown[],
    dropdown_properties: IDropdownProperties
): any[][] => mapData((datum, rowIndex) => R.map(column => {
    const realIndex = indices[rowIndex];

    let legacyDropdown: any = (
        (
            dropdown_properties &&
            dropdown_properties[column.id] &&
            (
                dropdown_properties[column.id].length > realIndex ?
                    dropdown_properties[column.id][realIndex] :
                    null
            )
        ) || column || { options: undefined }
    ).options;

    const conditional = columnConditionalDropdown.find((cs: any) => cs.id === column.id);
    const base = columnStaticDropdown.find((ss: any) => ss.id === column.id);

    const conditionalDropdowns = (conditional && conditional.dropdowns) || [];
    const staticDropdown = legacyDropdown || (base && base.dropdown);

    return getDropdown(astCache, conditionalDropdowns, datum, column.id, staticDropdown);
}, columns), data);

const getterFactory = memoizeOneFactory(getter);

const decoratedGetter = (_id: string): ((
    columns: VisibleColumns,
    data: Data,
    indices: Indices,
    columnConditionalDropdown: any,
    columnStaticDropdown: any,
    dropdown_properties: any
) => any[][]) => {
    const astCache = memoizerCache<[ColumnId, number], [string], SyntaxTree>(
        (query: string) => new SyntaxTree(query)
    );

    return getterFactory().bind(undefined, astCache);
};

export default memoizeOneFactory(decoratedGetter);
