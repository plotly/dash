import * as R from 'ramda';

import { memoizeOneFactory } from 'core/memoizer';

import { VisibleColumns, IVisibleColumn } from 'dash-table/components/Table/props';
import { SingleColumnSyntaxTree, MultiColumnsSyntaxTree, getSingleColumnMap } from 'dash-table/syntax-tree';

const cloneIf = (
    current: Map<string, SingleColumnSyntaxTree>,
    base: Map<string, SingleColumnSyntaxTree>
) => current === base ? new Map<string, SingleColumnSyntaxTree>(base) : current;

export default memoizeOneFactory((
    map: Map<string, SingleColumnSyntaxTree>,
    query: string,
    columns: VisibleColumns
): Map<string, SingleColumnSyntaxTree> => {
    const multiQuery = new MultiColumnsSyntaxTree(query);
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
        R.concat(
            Array.from(map.keys()),
            Array.from(reversedMap.keys())
        )
    );

    R.forEach(key => {
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
    }, keys);

    return newMap;
});

export const updateMap = (
    map: Map<string, SingleColumnSyntaxTree>,
    column: IVisibleColumn,
    value: any
): Map<string, SingleColumnSyntaxTree> => {
    const safeColumnId = column.id.toString();

    const newMap = new Map<string, SingleColumnSyntaxTree>(map);

    if (value && value.length) {
        newMap.set(safeColumnId, new SingleColumnSyntaxTree(value, column));
    } else {
        newMap.delete(safeColumnId);
    }

    return newMap;
};