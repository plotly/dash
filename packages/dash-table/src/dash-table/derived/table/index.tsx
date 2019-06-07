import * as R from 'ramda';

import { memoizeOne } from 'core/memoizer';

import CellFactory from 'dash-table/components/CellFactory';
import EdgeFactory from 'dash-table/components/EdgeFactory';
import FilterFactory from 'dash-table/components/FilterFactory';
import HeaderFactory from 'dash-table/components/HeaderFactory';
import { clearSelection } from 'dash-table/utils/actions';
import { ControlledTableProps, SetProps, SetState } from 'dash-table/components/Table/props';

import { SingleColumnSyntaxTree } from 'dash-table/syntax-tree';

const handleSetFilter = (
    setProps: SetProps,
    setState: SetState,
    filter_query: string,
    rawFilterQuery: string,
    map: Map<string, SingleColumnSyntaxTree>
) => {
    setProps({ filter_query, ...clearSelection });
    setState({ workFilter: { map, value: filter_query }, rawFilterQuery });
};

function filterPropsFn(propsFn: () => ControlledTableProps, setFilter: any) {
    const props = propsFn();

    return R.merge(props, { map: props.workFilter.map, setFilter });
}

function getter(
    cellFactory: CellFactory,
    filterFactory: FilterFactory,
    headerFactory: HeaderFactory,
    edgeFactory: EdgeFactory
): JSX.Element[][] {
    const cells: JSX.Element[][] = [];

    const edges = edgeFactory.createEdges();

    const dataCells = cellFactory.createCells(edges.dataEdges, edges.dataOpEdges);
    const filters = filterFactory.createFilters(edges.filterEdges, edges.filterOpEdges);
    const headers = headerFactory.createHeaders(edges.headerEdges, edges.headerOpEdges);

    cells.push(...headers);
    cells.push(...filters);
    cells.push(...dataCells);

    return cells;
}

export default (propsFn: () => ControlledTableProps) => {
    const setFilter = memoizeOne((
        setProps: SetProps,
        setState: SetState
    ) => handleSetFilter.bind(undefined, setProps, setState));

    const cellFactory = new CellFactory(propsFn);
    const filterFactory = new FilterFactory(() => {
        const props = propsFn();

        return filterPropsFn(propsFn, setFilter(props.setProps, props.setState));
    });
    const headerFactory = new HeaderFactory(propsFn);
    const edgeFactory = new EdgeFactory(propsFn);

    return getter.bind(undefined, cellFactory, filterFactory, headerFactory, edgeFactory);
};
