import * as R from 'ramda';

import {memoizeOneFactory} from 'core/memoizer';
import sort, {SortBy} from 'core/sorting';
import {
    ColumnId,
    Data,
    Datum,
    IDerivedData,
    SortAsNull,
    Columns,
    TableAction,
    IFilterAction
} from 'dash-table/components/Table/props';
import {QuerySyntaxTree} from 'dash-table/syntax-tree';

const getter = (
    columns: Columns,
    data: Data,
    filter_action: IFilterAction,
    filter_query: string,
    sort_action: TableAction,
    sort_by: SortBy = []
): IDerivedData => {
    const map = new Map<Datum, number>();
    R.addIndex<Datum>(R.forEach)((datum, index) => {
        map.set(datum, index);
    }, data);

    if (filter_action.type === TableAction.Native) {
        const tree = new QuerySyntaxTree(filter_query);

        data = tree.isValid ? tree.filter(data) : data;
    }

    const getNullyCases = (columnId: ColumnId): SortAsNull => {
        const column = R.find(c => c.id === columnId, columns);

        return (column && column.sort_as_null) || [];
    };

    const isNully = (value: any, columnId: ColumnId) =>
        R.isNil(value) || R.includes(value, getNullyCases(columnId));

    if (sort_action === TableAction.Native) {
        data = sort(data, sort_by, isNully);
    }

    // virtual_indices
    const indices = R.map(datum => map.get(datum) as number, data);

    return {data, indices};
};

export default memoizeOneFactory(getter);
