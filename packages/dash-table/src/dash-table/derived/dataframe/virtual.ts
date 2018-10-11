import * as R from 'ramda';

import { memoizeOneFactory } from 'core/memoizer';
import sort, { defaultIsNully, SortSettings } from 'core/sorting';
import SyntaxTree from 'core/syntax-tree';
import {
    Dataframe,
    Datum,
    Filtering,
    IDerivedDataframe,
    Sorting
} from 'dash-table/components/Table/props';

const getter = (
    dataframe: Dataframe,
    filtering: Filtering,
    filtering_settings: string,
    sorting: Sorting,
    sorting_settings: SortSettings = [],
    sorting_treat_empty_string_as_none: boolean
): IDerivedDataframe => {
    const map = new Map<Datum, number>();
    R.addIndex(R.forEach)((datum, index) => {
        map.set(datum, index);
    }, dataframe);

    if (filtering === 'fe' || filtering === true) {
        const tree = new SyntaxTree(filtering_settings);

        dataframe = tree.isValid ?
            tree.filter(dataframe) :
            dataframe;
    }

    const isNully = sorting_treat_empty_string_as_none ?
        (value: any) => value === '' || defaultIsNully(value) :
        undefined;

    if (sorting === 'fe' || sorting === true) {
        dataframe = sort(dataframe, sorting_settings, isNully);
    }

    // virtual_indices
    const indices = R.map(datum => map.get(datum) as number, dataframe);

    return { dataframe, indices };
};

export default memoizeOneFactory(getter);
