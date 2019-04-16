import * as R from 'ramda';

import { memoizeOneFactory } from 'core/memoizer';
import sort, { defaultIsNully, SortSettings } from 'core/sorting';
import {
    Data,
    Datum,
    Filtering,
    IDerivedData,
    Sorting
} from 'dash-table/components/Table/props';
import { QuerySyntaxTree } from 'dash-table/syntax-tree';

const getter = (
    data: Data,
    filtering: Filtering,
    filter: string,
    sorting: Sorting,
    sorting_settings: SortSettings = [],
    sorting_treat_empty_string_as_none: boolean
): IDerivedData => {
    const map = new Map<Datum, number>();
    R.addIndex(R.forEach)((datum, index) => {
        map.set(datum, index);
    }, data);

    if (filtering === 'fe' || filtering === true) {
        const tree = new QuerySyntaxTree(filter);

        data = tree.isValid ?
            tree.filter(data) :
            data;
    }

    const isNully = sorting_treat_empty_string_as_none ?
        (value: any) => value === '' || defaultIsNully(value) :
        undefined;

    if (sorting === 'fe' || sorting === true) {
        data = sort(data, sorting_settings, isNully);
    }

    // virtual_indices
    const indices = R.map(datum => map.get(datum) as number, data);

    return { data, indices };
};

export default memoizeOneFactory(getter);
