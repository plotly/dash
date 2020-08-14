import * as R from 'ramda';

import {memoizeOne} from 'core/memoizer';

import CellFactory from 'dash-table/components/CellFactory';
import EdgeFactory from 'dash-table/components/EdgeFactory';
import FilterFactory from 'dash-table/components/FilterFactory';
import HeaderFactory from 'dash-table/components/HeaderFactory';
import {clearSelection} from 'dash-table/utils/actions';
import {
    ControlledTableProps,
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

function propsAndMapFn(propsFn: () => ControlledTableProps, setFilter: any) {
    const props = propsFn();

    return R.merge(props, {map: props.workFilter.map, setFilter});
}

export default (propsFn: () => ControlledTableProps) => {
    const setFilter = memoizeOne((setProps: SetProps, setState: SetState) =>
        handleSetFilter.bind(undefined, setProps, setState)
    );

    const cellFactory = new CellFactory(propsFn);

    const augmentedPropsFn = () => {
        const props = propsFn();

        return propsAndMapFn(
            propsFn,
            setFilter(props.setProps, props.setState)
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
