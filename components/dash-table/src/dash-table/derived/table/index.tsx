import * as R from 'ramda';

import {memoizeOne} from 'core/memoizer';

import CellFactory from 'dash-table/components/CellFactory';
import EdgeFactory from 'dash-table/components/EdgeFactory';
import FilterFactory from 'dash-table/components/FilterFactory';
import HeaderFactory from 'dash-table/components/HeaderFactory';
import {clearSelection} from 'dash-table/utils/actions';
import {
    ControlledTableProps,
    FilterCase,
    IColumn,
    SetProps,
    SetState
} from 'dash-table/components/Table/props';

import {SingleColumnSyntaxTree} from 'dash-table/syntax-tree';

const handleSetFilter = (
    setProps: SetProps,
    setState: SetState,
    filter_query: string,
    rawFilterQuery: string,
    map: Map<string, SingleColumnSyntaxTree>
) => {
    setProps({filter_query, ...clearSelection});
    setState({workFilter: {map, value: filter_query}, rawFilterQuery});
};

function propsAndMapFn(
    propsFn: () => ControlledTableProps,
    setFilter: any,
    toggleFilterOptions: (column: IColumn) => IColumn
) {
    const props = propsFn();

    return R.mergeRight(props, {
        map: props.workFilter.map,
        setFilter,
        toggleFilterOptions
    });
}

export default (propsFn: () => ControlledTableProps) => {
    const setFilter = memoizeOne((setProps: SetProps, setState: SetState) =>
        handleSetFilter.bind(undefined, setProps, setState)
    );

    const toggleFilterOptions = memoizeOne(
        (setProps: SetProps, columns: IColumn[]) => (column: IColumn) => {
            const newColumns = [...columns];
            const iColumn = columns.indexOf(column);

            const newColumn = {...newColumns[iColumn]};
            newColumn.filter_options = {
                ...newColumn.filter_options,
                case:
                    newColumn.filter_options.case === FilterCase.Insensitive
                        ? FilterCase.Sensitive
                        : FilterCase.Insensitive
            };

            newColumns.splice(iColumn, 1, newColumn);

            setProps({columns: newColumns});

            return newColumn;
        }
    );

    const cellFactory = new CellFactory(propsFn);

    const augmentedPropsFn = () => {
        const props = propsFn();

        return propsAndMapFn(
            propsFn,
            setFilter(props.setProps, props.setState),
            toggleFilterOptions(props.setProps, props.columns)
        );
    };

    const filterFactory = new FilterFactory(augmentedPropsFn);
    const headerFactory = new HeaderFactory(augmentedPropsFn);
    const edgeFactory = new EdgeFactory(propsFn);

    const merge = memoizeOne(
        (
            data: JSX.Element[][],
            filters: JSX.Element[][],
            headers: JSX.Element[][]
        ) => {
            const cells: JSX.Element[][] = [];

            cells.push(...headers);
            cells.push(...filters);
            cells.push(...data);

            return cells;
        }
    );

    return () => {
        const edges = edgeFactory.createEdges();

        const dataCells = cellFactory.createCells(
            edges.dataEdges,
            edges.dataOpEdges
        );
        const filters = filterFactory.createFilters(
            edges.filterEdges,
            edges.filterOpEdges
        );
        const headers = headerFactory.createHeaders(
            edges.headerEdges,
            edges.headerOpEdges
        );

        return merge(dataCells, filters, headers);
    };
};
