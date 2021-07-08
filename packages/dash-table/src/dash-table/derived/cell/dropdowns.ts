import * as R from 'ramda';

import {memoizeOne} from 'core/memoizer';
import memoizerCache from 'core/cache/memoizer';

import {
    ColumnId,
    ConditionalDropdowns,
    Data,
    DataDropdowns,
    Datum,
    IConditionalDropdown,
    IDropdown,
    Indices,
    IColumn,
    StaticDropdowns,
    Columns
} from 'dash-table/components/Table/props';
import {QuerySyntaxTree} from 'dash-table/syntax-tree';
import {ifColumnId} from 'dash-table/conditional';

const mapData = R.addIndex<Datum, (IDropdown | undefined)[]>(R.map);

export default () => new Dropdowns().get;

class Dropdowns {
    /**
     * Return the dropdown for each cell in the table.
     */
    get = memoizeOne(
        (
            columns: Columns,
            data: Data,
            indices: Indices,
            conditionalDropdowns: ConditionalDropdowns,
            staticDropdowns: StaticDropdowns,
            dataDropdowns: DataDropdowns
        ) =>
            mapData(
                (datum, rowIndex) =>
                    R.map(column => {
                        const realIndex = indices[rowIndex];

                        const appliedStaticDropdown =
                            (dataDropdowns &&
                                dataDropdowns.length > realIndex &&
                                dataDropdowns[realIndex] &&
                                dataDropdowns[realIndex][column.id]) ||
                            staticDropdowns[column.id];

                        return this.dropdown.get(column.id, rowIndex)(
                            appliedStaticDropdown,
                            conditionalDropdowns,
                            column,
                            datum
                        );
                    }, columns),
                data
            )
    );

    /**
     * Returns the highest priority dropdown from the
     * applicable dropdowns.
     */
    private readonly dropdown = memoizerCache<[ColumnId, number]>()(
        (
            base: IDropdown | undefined,
            conditionals: ConditionalDropdowns,
            column: IColumn,
            datum: Datum
        ) => {
            const conditional = R.findLast(
                ([cd, i]) =>
                    ifColumnId(cd.if, column.id) &&
                    (R.isNil(cd.if) ||
                        R.isNil(cd.if.filter_query) ||
                        this.evaluation.get(column.id, i)(
                            this.ast.get(column.id, i)(cd.if.filter_query),
                            datum
                        )),
                R.addIndex<
                    IConditionalDropdown,
                    [IConditionalDropdown, number]
                >(R.map)((cd, i) => [cd, i], conditionals)
            );

            return (conditional && conditional[0]) || base || undefined;
        }
    );

    /**
     * Get the query's AST.
     */
    private readonly ast = memoizerCache<[ColumnId, number]>()(
        (query: string) => new QuerySyntaxTree(query)
    );

    /**
     * Evaluate if the query matches the cell's data.
     */
    private readonly evaluation = memoizerCache<[ColumnId, number]>()(
        (ast: QuerySyntaxTree, datum: Datum) => ast.evaluate(datum)
    );
}
