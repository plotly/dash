import * as R from 'ramda';

import {memoizeOneFactory} from 'core/memoizer';

import {
    Columns,
    IColumn,
    SetFilter,
    FilterLogicalOperator
} from 'dash-table/components/Table/props';
import {
    SingleColumnSyntaxTree,
    MultiColumnsSyntaxTree,
    getMultiColumnQueryString,
    getSingleColumnMap
} from 'dash-table/syntax-tree';

const cloneIf = (
    current: Map<string, SingleColumnSyntaxTree>,
    base: Map<string, SingleColumnSyntaxTree>
) =>
    current === base ? new Map<string, SingleColumnSyntaxTree>(base) : current;

export default memoizeOneFactory(
    (
        map: Map<string, SingleColumnSyntaxTree>,
        operator: FilterLogicalOperator,
        query: string,
        columns: Columns
    ): Map<string, SingleColumnSyntaxTree> => {
        const multiQuery = new MultiColumnsSyntaxTree(query, operator);
        const reversedMap = getSingleColumnMap(multiQuery, columns);
        /*
         * Couldn't process the query, just use the previous value.
         */
        if (!reversedMap) {
            return map;
        }

        /* Mapping multi-column to single column queries will expand
         * compressed forms. If the new ast query is equal to the
         * old one, keep the old one instead.
         *
         * If the value was changed by the user, the current ast will
         * have been modified already and the UI experience will also
         * be consistent in that case.
         */
        let newMap = map;

        const keys = R.uniq(
            R.concat(Array.from(map.keys()), Array.from(reversedMap.keys()))
        );

        keys.forEach(key => {
            const ast = map.get(key);
            const reversedAst = reversedMap.get(key);

            if (R.isNil(reversedAst)) {
                newMap = cloneIf(newMap, map);
                newMap.delete(key);
            } else if (
                R.isNil(ast) ||
                reversedAst.toQueryString() !== ast.toQueryString()
            ) {
                newMap = cloneIf(newMap, map);
                newMap.set(key, reversedAst);
            }
        });

        return newMap;
    }
);

function updateMap(
    map: Map<string, SingleColumnSyntaxTree>,
    column: IColumn,
    value: any
) {
    const id = column.id.toString();
    const newMap = new Map<string, SingleColumnSyntaxTree>(map);

    if (value && value.length) {
        newMap.set(id, new SingleColumnSyntaxTree(value, column));
    } else {
        newMap.delete(id);
    }

    return newMap;
}

function updateState(
    map: Map<string, SingleColumnSyntaxTree>,
    operator: FilterLogicalOperator,
    setFilter: SetFilter
) {
    const asts = Array.from(map.values());
    const globalFilter = getMultiColumnQueryString(asts, operator);

    const rawGlobalFilter = R.map(
        ast => ast.query,
        R.filter<SingleColumnSyntaxTree>(ast => Boolean(ast?.query))(asts)
    ).join(operator === FilterLogicalOperator.And ? ' && ' : ' || ');

    setFilter(globalFilter, rawGlobalFilter, map);
}

export const updateColumnFilter = (
    map: Map<string, SingleColumnSyntaxTree>,
    column: IColumn,
    operator: FilterLogicalOperator,
    value: any,
    setFilter: SetFilter
) => {
    map = updateMap(map, column, value);
    updateState(map, operator, setFilter);
};

export const clearColumnsFilter = (
    map: Map<string, SingleColumnSyntaxTree>,
    columns: Columns,
    operator: FilterLogicalOperator,
    setFilter: SetFilter
) => {
    columns.forEach(column => {
        map = updateMap(map, column, '');
    });

    updateState(map, operator, setFilter);
};
